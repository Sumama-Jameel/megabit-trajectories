# Feedback report

## Tests

The harness ran the project's suite three times with `python -m pytest` (rootdir `/workspace`, configfile `pyproject.toml`, testpaths `tests`). All three runs had `exit_code=0`.

Each run collected 1355 items and finished with:

```
================= 1347 passed, 7 skipped, 1 xfailed in 16.06s ==================
```

Run 2: `1347 passed, 7 skipped, 1 xfailed in 15.15s`
Run 3: `1347 passed, 7 skipped, 1 xfailed in 16.10s`

So: 1355 collected, 1347 passed, 0 failed, 7 skipped, 1 xfailed. The skips are environment/platform based (`requires Python 3.13+`, `Pre-3.10 only.`, `Requires pyright.`, PyPy-only slots) and the single xfail is `tests/test_setattr.py::TestSetAttr::test_slotted_confused`. No test failed in any run.

## What is missing

Nothing. The ticket asked for one behavior change to `deep_mapping`: allow passing only a key validator or only a value validator, and raise a clear error only when both are omitted. Reading the staged diff (`git diff --cached`), that is implemented:

- `src/attr/validators.py:381-383` — `key_validator` and `value_validator` now default to `None` and are wrapped in `validator=optional(is_callable())`.
- `src/attr/validators.py:392-401` — `__call__` handles key-only, value-only, and both.
- `src/attr/validators.py:428-430` — raises `ValueError("At least one of key_validator or value_validator must be provided")` when both are `None`.
- `src/attr/validators.pyi:68-85` — three `@overload`s covering both-positional, key-only, and value-only.

The tests and typing examples that exercise this (`tests/test_validators.py` `TestDeepMapping`, `tests/typing_example.py`) were already present in `HEAD`; the coder's diff is source-only, which is fine because the ticket did not ask for new docs, changelog, or test files.

## Why it fails

No test fails. All three harness runs report `0 failed`, `exit_code=0`.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a `deep_mapping` where a user can supply just a key check or just a value check, and only gets an error if they supply neither. The product that exists now matches that. A user calling `deep_mapping(key_validator=...)` gets only keys checked; a user calling `deep_mapping(value_validator=...)` gets only values checked; a user calling `deep_mapping()` with neither gets a clear `ValueError` naming both parameters instead of a confusing `TypeError`. Passing a non-callable still raises `TypeError` because of the `optional(is_callable())` validators, so the earlier failure mode for bad inputs is preserved. Type checkers see three overloads in `src/attr/validators.pyi`, so key-only and value-only calls type-check. There is no user-visible gap between the described product and the current one that I could find from the code I read and the harness results.
