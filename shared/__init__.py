"""
shared — cowork foundation layer.

Public API re-exported here so packages can do:
    from shared import models, store, llm

Or import specific symbols:
    from shared.models import Fact, AutoCaptureResult, KeelConfig
    from shared.store import load_projects, save_fact, match_project_by_cwd
    from shared.llm import extract, Model, LLMExtractionError
"""
from shared import llm, models, store

__all__ = ["models", "store", "llm"]
