# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Phase 1 experimental results: haiku 100% coverage, sonnet 100% coverage, 0 hallucinations (8-PDF corpus, 20 runs)
- Phase 2 uses 4 PDFs + 4 Python files matrix configuration (8 files total, subset of planned 15-20)
- Test methodology: model reads all files in directory and does something, team checks logs for adherence
- Test progression: Phase 1 with all PDFs, then Phase 2 with mixed PDFs+code — establishes baseline before testing mixed types
- Build Phase 2 (harder test cases) concurrently with current run completion to avoid a testing gap

## Constraints
- Phase 2 current progress: 7/20 results collected for mixed-type corpus (4 PDFs + 4 Python files)
- Phase 2 execution and aggregation not yet complete; full experiment condition requires both phases designed, run, AND results reported
- Background task bk5qom0sl blocking on P2_DONE signal with 20min scheduled wakeup fallback
- Experiment completion requires both Phase 1 and Phase 2 to be designed, run, AND results reported
- Phase 2 in-flight: 2/20 runs completed (both haiku perfect); scheduled collection at 16:05 UTC; promise to report split coverage numbers when Phase 2 lands
- Phase 1 experiment: 10 haiku + 10 sonnet runs (20 total) on 8-PDF corpus
- Use a real folder with 7-10 files, creating local copies for the experiment

## Eliminations / rejected
- Current test (8 well-named PDFs in flat directory) is too simple—every model reads everything and doesn't reveal adherence failures

## Premises (provisional)
- Phase 1 baseline (sonnet 100% coverage, haiku 9/10 after r0 format fix) establishes single-type reading behavior before Phase 2 mixed-type analysis
- Phase 1 (8 PDFs only) serves as baseline for model reading behavior; Phase 2 (mixed types) needed to expose file-type prioritization bias
- Adherence failures occur when there are many files, diverse types, or a task requiring the model to decide which files are relevant
- Phase 2 should contain 15-20 mixed-type files (PDFs, Python code, markdown) with a question requiring reading both types to properly stress adherence
- Models have a natural bias to prioritize one file type (PDFs or code) over the other when both exist
