# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Default FILE_UPLOAD_PERMISSION should be set to 0o644

## Constraints
- Do NOT edit or add test files when fixing this bug
- tempfile.NamedTemporaryFile + os.rename sequence creates 0o0600 permissions on some systems (CentOS 7.4, Python 3.6.5), causing inconsistency with other upload paths

## Premises (provisional)
- File permission inconsistency depends on uploaded file size and which temporary storage handler is used (MemoryUploadedFile vs TemporaryUploadedFile)
