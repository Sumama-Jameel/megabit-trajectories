# Feedback report

## Tests

The pipeline ran the project's test suite three times; I did not run any tests myself.

Command (identical in all three pipeline runs): `python -m pytest`

- Run 1: `62397 passed, 427 deselected in 168.53s (0:02:48)` — exit_code=0
- Run 2: `62397 passed, 427 deselected in 134.18s (0:02:14)` — exit_code=0
- Run 3: `62397 passed, 427 deselected in 162.29s (0:02:42)` — exit_code=0

Totals: 62397 tests passed, 0 failed (427 deselected) in every run. All three runs were classified `substantive` with exit_code=0. No failing test output appears in any run.

I also confirmed the two relevant tests exist in the workspace: `tests/test_pylock_select.py:310` `def test_empty_tags_selects_sdist_instead_of_host_compatible_wheel()` and `tests/test_pylock_select.py:324` `def test_empty_tags_rejects_wheel_only_lock()`.

## What is missing

Nothing that the ticket asked for is missing, as far as I can see from the diff and the passing suite.

- The behavior change is present. `git diff HEAD -- src/packaging/pylock.py` shows the old line replaced by:
  `sys_tags() if tags is None else tags` (`src/packaging/pylock.py:796`).
- The user-facing "help text" is updated. The docstring now says: "Passing an empty sequence for *tags* / means no wheels are acceptable, so an error is raised if no source / distribution is available." (`pylock.py`, diff hunk at 765-770) and a versionchanged note "An empty *tags* sequence now means no wheels are acceptable instead / of falling back to ``packaging.tags.sys_tags()``." (`pylock.py`, diff hunk at 787-793).
- A changelog entry was added under "Behavior adaptations": "Passing an empty sequence of tags to :meth:`Pylock.select() ...` now means no wheels are acceptable instead of falling back to the host's tags. A source distribution is selected when available, and an error is raised when only wheels are present." (`CHANGELOG.rst`, diff hunk at 18-23).

I am not raising style, formatting, or extra-documentation items as missing, because the ticket did not ask for them and the suite passes.

## Why it fails

No test failed. All three pipeline runs report `62397 passed, 427 deselected` with exit_code=0, so there is no failing test to explain.

Uncertainty I will state plainly: I did not independently exercise the new empty-`tags` behavior outside the harness suite, so my confidence in the exact runtime message ("No wheel found matching the provided tags ... and no sdist available as a fallback", `src/packaging/pylock.py:933-936`) rests on the passing tests, not on a run I performed. This is not evidence of a defect.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a `Pylock.select()` that treated an empty tag list as "use the host's tags", so a lock file listing both a host-compatible wheel and an sdist would silently hand back the host wheel, and a wheel-only lock would also hand back the host wheel. The ticket asks for an empty tag list to mean "no wheels are acceptable".

What exists now, based on the diff I read and the passing suite:

- When `tags` is omitted (`None`), `Pylock.select()` still uses the host's `packaging.tags.sys_tags()` (`src/packaging/pylock.py:796`), so existing callers that pass no tags keep the same behavior.
- When `tags` is an empty sequence, the selector is built from that empty sequence rather than from host tags (`src/packaging/pylock.py:796`). Because no wheel can match an empty tag set, wheel selection yields nothing.
- With an empty tag list and a lock that includes a source distribution, the source distribution is selected instead of a host-compatible wheel. This is exercised by `tests/test_pylock_select.py:310` `test_empty_tags_selects_sdist_instead_of_host_compatible_wheel()`, which passed.
- With an empty tag list and a lock that has only wheels, selection fails with an error rather than silently using the host wheel. The error path is `"No wheel found matching the provided tags " ... "and no sdist available as a fallback"` (`src/packaging/pylock.py:933-936`), exercised by `tests/test_pylock_select.py:324` `test_empty_tags_rejects_wheel_only_lock()`, which passed.
- The docstring the user reads (`Pylock.select()`) now explains the empty-*tags* meaning, and the project changelog records the change under "Behavior adaptations".

So the product the ticket describes — empty tags means no wheels, sdist chosen when available, error when not — matches the code in the workspace, and the whole suite passes.