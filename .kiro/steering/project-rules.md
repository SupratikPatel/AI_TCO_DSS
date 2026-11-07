---
inclusion: always
---

# Project Rules

1. At the start of every session, read `progress.md` before reading or modifying any other project file.
2. Work test-first: for every acceptance criterion id the task covers, add at least one test, run the tests and observe at least one failure before writing the implementation that makes them pass.
3. Attach a Provenance_Record (`source_id`, Source_Tier, ISO 8601 access date) to every numeric value in the Catalog.
4. When both a measured value (Benchmark_Record) and a formula value exist for the same metric, use the measured value.
5. Use USD as the default currency.
6. Modify only files listed in the current Task_Scope.
7. Record every detected data contradiction in `specs/07_DATA_CORRECTIONS.md` with old value, new value, sources and decision date.
8. Before finishing a task, make sure the task's new tests pass and the full `pytest` suite reports zero failures and zero errors, then update `progress.md` and the Next Session Prompt; only then mark the task `done`.
