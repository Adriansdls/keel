"""
shared/llm.py — Dual-backend LLM extraction for the cowork stack.

Default backend: subprocess via `claude` CLI — uses Claude subscription,
no API key required, works for any non-technical user with Claude Code installed.

Optional backend: Anthropic SDK — opt-in, requires ANTHROPIC_API_KEY,
uses tool_use for guaranteed-valid JSON (zero parse failure).

No regex anywhere. Subprocess path uses schema-in-prompt + direct json.loads()
with one retry. SDK path uses tool_use — parse failure is structurally impossible.

Usage:
    from shared.llm import extract, Model
    from shared.models import AutoCaptureResult

    result = extract(
        system_prompt="Extract work-tracking events from this conversation.",
        schema=AutoCaptureResult,
        context=transcript_text,
        model=Model.fast,
    )
    # result is a validated AutoCaptureResult instance
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import sys
import textwrap
from enum import Enum
from pathlib import Path
from typing import Optional, TypeVar

from pydantic import BaseModel

# Lazy import — only loaded when backend=api
_anthropic: Optional[object] = None

T = TypeVar("T", bound=BaseModel)


# ══════════════════════════════════════════════════════════════════════════════
# Public types
# ══════════════════════════════════════════════════════════════════════════════

class Model(str, Enum):
    fast  = "fast"    # → haiku  — auto-capture, SWM Stop hook, entropy brief
    smart = "smart"   # → sonnet — premise check, outcome loop


class LLMExtractionError(Exception):
    """
    Raised when extraction fails after retry.
    All hooks must catch this and exit 0 (fail-open).
    """


# ══════════════════════════════════════════════════════════════════════════════
# Config cache
# ══════════════════════════════════════════════════════════════════════════════

_cached_config: Optional[object] = None


def _config():
    global _cached_config
    if _cached_config is None:
        # Lazy import to avoid circular dependency at module level
        from shared.store import load_config
        _cached_config = load_config()
    return _cached_config


def _resolve_model(model: Model) -> str:
    cfg = _config()
    if model == Model.fast:
        return cfg.llm.fast_model
    return cfg.llm.smart_model


def _backend():
    from shared.models import LLMBackend
    return _config().llm.backend if hasattr(_config().llm, "backend") else _config().llm.mode


def _timeout(model: Model) -> int:
    cfg = _config()
    return cfg.llm.timeout_fast if model == Model.fast else cfg.llm.timeout_smart


# ══════════════════════════════════════════════════════════════════════════════
# Public entry point
# ══════════════════════════════════════════════════════════════════════════════

def extract(
    system_prompt: str,
    schema: type[T],
    context: str,
    model: Model = Model.fast,
) -> T:
    """
    Single entry point for all LLM extraction in the cowork stack.

    Returns a validated Pydantic instance of `schema`.
    Raises LLMExtractionError on failure (hooks should catch → fail-open).
    """
    from shared.models import LLMBackend
    backend = _backend()

    if backend == LLMBackend.api:
        return _extract_sdk(system_prompt, schema, context, model)
    else:
        return _extract_subprocess(system_prompt, schema, context, model)


# ══════════════════════════════════════════════════════════════════════════════
# Subprocess backend (default)
# ══════════════════════════════════════════════════════════════════════════════

_JSON_RULES = """\
IMPORTANT OUTPUT FORMAT RULES — follow exactly:
- Respond with ONLY a valid JSON object.
- Start your response with { and end with }
- No prose, no explanation, no markdown, no code fences.
- Every field in the schema is required unless marked optional."""


def _describe_type(info: dict, defs: dict) -> str:
    """Produce a compact type string including enum values when present."""
    # Resolve $ref
    if "$ref" in info:
        ref_name = info["$ref"].split("/")[-1]
        info = defs.get(ref_name, {})

    # Enum — show exact allowed values (critical for correctness)
    if "enum" in info:
        vals = ", ".join(f'"{v}"' for v in info["enum"])
        return f"one of: {vals}"

    # anyOf (Optional[X], union types)
    if "anyOf" in info:
        non_null = [i for i in info["anyOf"] if i.get("type") != "null"]
        if len(non_null) == 1:
            return _describe_type(non_null[0], defs)
        return " | ".join(_describe_type(i, defs) for i in non_null)

    # Array — describe items
    if info.get("type") == "array":
        items = info.get("items", {})
        return f"array of {_describe_type(items, defs)}"

    # Object with properties — recurse one level
    if info.get("type") == "object" and "properties" in info:
        sub = ", ".join(f"{k}: {_describe_type(v, defs)}" for k, v in info["properties"].items())
        return f"object({sub})"

    return info.get("type", "any")


def _render_schema(schema: type[BaseModel]) -> str:
    """
    Render a compact, human-readable schema description for inclusion in the prompt.
    Crucially: shows exact enum values so the model uses the right strings.
    No regex, no $ref in output — everything resolved to plain text.
    """
    full = schema.model_json_schema()
    defs = full.get("$defs", {})
    props = full.get("properties", {})
    required = set(full.get("required", []))

    lines = [f"JSON Schema ({full.get('title', schema.__name__)})"]
    lines.append("Fields:")
    for name, info in props.items():
        typ = _describe_type(info, defs)
        req = "required" if name in required else "optional"
        desc = info.get("description", "")
        line = f"  {name} ({req}): {typ}"
        if desc:
            line += f"  — {desc}"
        lines.append(line)

    return "\n".join(lines)


def _build_prompt(system_prompt: str, schema: type[BaseModel], context: str) -> str:
    schema_desc = _render_schema(schema)
    # Truncate context to avoid hitting model limits (haiku: 200k, but we keep hooks cheap)
    max_context = 5000
    if len(context) > max_context:
        context = "...[truncated]...\n" + context[-max_context:]

    return "\n\n".join([
        system_prompt.strip(),
        _JSON_RULES,
        schema_desc,
        f"Text to analyze:\n{context}",
    ])


def _build_retry_prompt(system_prompt: str, schema: type[BaseModel],
                        context: str, bad_response: str) -> str:
    schema_desc = _render_schema(schema)
    max_context = 5000
    if len(context) > max_context:
        context = "...[truncated]...\n" + context[-max_context:]

    bad_excerpt = bad_response[:300]
    return "\n\n".join([
        system_prompt.strip(),
        f"Your previous response was not valid JSON. I received:\n{bad_excerpt}\n\n"
        f"Try again. Output ONLY the JSON object — nothing else.",
        _JSON_RULES,
        schema_desc,
        f"Text to analyze:\n{context}",
    ])


def _safe_env() -> dict:
    """
    Strip API keys from the environment before passing to subprocess.
    Forces the CLI to use subscription auth.
    """
    strip = {"ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"}
    return {k: v for k, v in os.environ.items() if k not in strip}


def _strip_code_fences(text: str) -> str:
    """
    Remove markdown code fences if present.
    Deterministic string operation — no regex.
    Handles: ```json\n{...}\n``` and ```\n{...}\n```
    """
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Drop first line (```json or ```) and last line (```)
        if len(lines) >= 3 and lines[-1].strip() == "```":
            return "\n".join(lines[1:-1]).strip()
        # Malformed fence — return as-is and let json.loads catch it
    return stripped


def _call_subprocess(prompt: str, resolved_model: str, timeout: int) -> str:
    """
    Call `claude -p` and return the raw result string.
    Uses a temp cwd so claude CLI finds no project-level settings to conflict with.
    Raises LLMExtractionError on failure.
    """
    try:
        with tempfile.TemporaryDirectory() as tmp_cwd:
            result = subprocess.run(
                [
                    "claude", "-p",
                    "--model", resolved_model,
                    "--output-format", "json",
                    prompt,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                stdin=subprocess.DEVNULL,
                cwd=tmp_cwd,   # neutral cwd — no project hooks, no auth conflicts
            )
    except FileNotFoundError:
        raise LLMExtractionError(
            "⚠  keel needs Claude Code to be installed.\n"
            "   Download it at: claude.ai/code\n"
            "   Once installed, try again."
        )
    except subprocess.TimeoutExpired:
        raise LLMExtractionError(f"LLM call timed out after {timeout}s")

    if result.returncode != 0:
        stderr = result.stderr.strip()[:200]
        raise LLMExtractionError(f"claude CLI returned exit {result.returncode}: {stderr}")

    stdout = result.stdout.strip()
    if not stdout:
        raise LLMExtractionError("claude CLI returned empty output")

    # Unwrap the --output-format json envelope: {"type": "result", "result": "..."}
    try:
        outer = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise LLMExtractionError(f"Could not parse CLI JSON envelope: {e}") from e

    # Check for usage/login issues
    raw = outer.get("result", "")
    if "usage limit" in raw.lower() or "rate limit" in raw.lower():
        raise LLMExtractionError(f"Claude usage/rate limit hit: {raw[:100]}")
    if "not logged in" in raw.lower() or "please run /login" in raw.lower():
        raise LLMExtractionError(
            "Claude is not logged in. Open Claude Code and run /login, then try again."
        )

    return raw


def _parse_and_validate(raw: str, schema: type[T]) -> T:
    """
    Direct json.loads() — no regex.
    Raises json.JSONDecodeError or pydantic.ValidationError on failure.
    """
    data = json.loads(_strip_code_fences(raw))
    return schema.model_validate(data)


def _extract_subprocess(
    system_prompt: str,
    schema: type[T],
    context: str,
    model: Model,
) -> T:
    resolved = _resolve_model(model)
    timeout = _timeout(model)

    # Attempt 1
    prompt = _build_prompt(system_prompt, schema, context)
    raw = _call_subprocess(prompt, resolved, timeout)
    try:
        return _parse_and_validate(raw, schema)
    except (json.JSONDecodeError, Exception):
        pass  # fall through to retry

    # Attempt 2 — stricter prompt, same model
    retry_prompt = _build_retry_prompt(system_prompt, schema, context, raw)
    raw2 = _call_subprocess(retry_prompt, resolved, timeout)
    try:
        return _parse_and_validate(raw2, schema)
    except Exception as e:
        raise LLMExtractionError(
            f"Failed to extract {schema.__name__} after retry. "
            f"Last error: {e}. Last response: {raw2[:200]}"
        ) from e


# ══════════════════════════════════════════════════════════════════════════════
# SDK backend (opt-in)
# ══════════════════════════════════════════════════════════════════════════════

def _load_anthropic():
    global _anthropic
    if _anthropic is None:
        try:
            import anthropic as _ant
            _anthropic = _ant
        except ImportError:
            raise LLMExtractionError(
                "The 'anthropic' package is required for api mode.\n"
                "Install it: pip install anthropic\n"
                "Or switch to mode: subscription in ~/.keel/config.yaml"
            )
    return _anthropic


def _extract_sdk(
    system_prompt: str,
    schema: type[T],
    context: str,
    model: Model,
) -> T:
    """
    Uses tool_use → Claude is forced to return JSON matching the schema.
    Zero parse failure possible.
    """
    ant = _load_anthropic()
    cfg = _config()
    api_key = os.environ.get(cfg.llm.api_key_env)
    if not api_key:
        raise LLMExtractionError(
            f"API key not found in environment variable {cfg.llm.api_key_env!r}.\n"
            "Set it or switch to mode: subscription in ~/.keel/config.yaml"
        )

    client = ant.Anthropic(api_key=api_key)
    resolved = _resolve_model(model)

    # Convert Pydantic schema → JSON Schema for tool definition
    json_schema = schema.model_json_schema()
    # Strip $defs into a flat schema if possible (Anthropic requires no $ref in tool schemas)
    json_schema = _flatten_schema(json_schema)

    response = client.messages.create(
        model=resolved,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": context[-5000:]}],
        tools=[{
            "name": "extract",
            "description": f"Extract structured {schema.__name__} from the provided text.",
            "input_schema": json_schema,
        }],
        tool_choice={"type": "tool", "name": "extract"},  # force tool use — no prose possible
    )

    # Tool response is already a dict — no parsing needed
    tool_block = next(
        (b for b in response.content if b.type == "tool_use" and b.name == "extract"),
        None,
    )
    if tool_block is None:
        raise LLMExtractionError("SDK response did not include tool_use block")

    return schema.model_validate(tool_block.input)


def _flatten_schema(schema: dict) -> dict:
    """
    Inline $defs references into the main schema.
    Anthropic's tool API doesn't support $ref/$defs in input_schema.
    Simple single-level inlining — sufficient for all cowork schemas.
    """
    defs = schema.pop("$defs", {})
    if not defs:
        return schema

    def resolve(node: object) -> object:
        if isinstance(node, dict):
            if "$ref" in node:
                ref_name = node["$ref"].split("/")[-1]
                resolved = defs.get(ref_name, {})
                return resolve(dict(resolved))
            return {k: resolve(v) for k, v in node.items()}
        if isinstance(node, list):
            return [resolve(i) for i in node]
        return node

    return resolve(schema)


# ══════════════════════════════════════════════════════════════════════════════
# Availability check (called by install.sh and hook startup)
# ══════════════════════════════════════════════════════════════════════════════

def check_claude_available() -> bool:
    """Return True if `claude` CLI is on PATH."""
    import shutil
    return shutil.which("claude") is not None


def assert_claude_available() -> None:
    """
    Print a friendly error and exit 1 if claude CLI is not found.
    For use at hook startup — never raises a stack trace.
    """
    if not check_claude_available():
        print(
            "\n⚠  keel needs Claude Code to be installed.\n"
            "   Download it at: claude.ai/code\n"
            "   Once installed, reopen your terminal.\n",
            file=sys.stderr,
        )
        sys.exit(1)
