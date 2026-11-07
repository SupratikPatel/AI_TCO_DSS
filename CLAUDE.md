# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.


Git Rules
Never push or commit, just git add the required files, the user will review and push themselves

## Project Rules

1. At the start of every session, read `progress.md` before reading or modifying any other project file.
2. Work test-first: for every acceptance criterion id the task covers, add at least one test, run the tests and observe at least one failure before writing the implementation that makes them pass.
3. Attach a Provenance_Record (`source_id`, Source_Tier, ISO 8601 access date) to every numeric value in the Catalog.
4. When both a measured value (Benchmark_Record) and a formula value exist for the same metric, use the measured value.
5. Use USD as the default currency.
6. Modify only files listed in the current Task_Scope.
7. Record every detected data contradiction in `specs/07_DATA_CORRECTIONS.md` with old value, new value, sources and decision date.
8. Before finishing a task, make sure the task's new tests pass and the full `pytest` suite reports zero failures and zero errors, then update `progress.md` and the Next Session Prompt; only then mark the task `done`.

Streamlit work: before creating or changing any Streamlit code (files under `src/ai_tco_dss/ui/` or AppTest tests), load the `developing-with-streamlit` agent skill and follow it; details and the fallback path are in `.kiro/steering/streamlit-ui.md`.
