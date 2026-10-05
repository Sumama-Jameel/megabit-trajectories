# Feedback report

## Tests

I did not run any tests myself (the pipeline owns test runs). The harness ran the project
suite three times. Command: `python -m pytest`. Result each time: **62333 passed, 0 failed,
427 deselected**, `exit_code=0`.

Real output excerpt, identical in all three runs:

```
collected 62760 items / 427 deselected / 62333 selected
...
=============== 62333 passed, 427 deselected in 79.37s (0:01:19) ===============
=============== 62333 passed, 427 deselected in 80.25s (0:01:20) ===============
=============== 62333 passed, 427 deselected in 82.66s (0:01:22) ===============
```

The tests that cover this change are in `tests/test_metadata.py`, and they pass in that run:
`test_from_email_unparsed` (`tests/test_metadata.py:364`, asserts 4 exceptions: `hello`,
`metadata-version`, `name`, `version`), `test_from_email_empty_metadata_uses_from_email_error_message`
(`tests/test_metadata.py:399`, asserts `.message == "invalid or unparsed metadata"` and fields
`metadata-version`, `name`, `version`), `test_from_email_unparsed_valid_field_name`
(`tests/test_metadata.py:392`), `test_from_email_validate` (`tests/test_metadata.py:377`).

## What is missing

Nothing the ticket asked for. `git status --porcelain` shows only `CHANGELOG.rst` and
`src/packaging/metadata.py` modified (`git diff --cached --stat`: `33 insertions(+),
13 deletions(-)`). Each ticket point is present in the diff:

1. The unparsed loop moved out of `_ErrorCollector().on_exit(...)` into a plain
   `for unparsed_key in unparsed:` loop guarded only by `if validate:`, and both exit paths
   now call `collector.finalize("invalid or unparsed metadata")`. The old heading
   `"unparsed"` and `on_exit` are gone from `from_email`.
2. The required-field group is no longer returned early. The `except ExceptionGroup` block
   now does `collector.errors.extend(...)` over `exc_group.exceptions`, so those errors reach
   the same report.
3. Unreadable fields are filtered out of that merge with
   `if not (isinstance(exc, InvalidMetadata) and exc.field in unparsed)`, so a field that is
   both unreadable and missing/invalid is reported once.
4. Clean input still returns the parsed object: `ins = cls.from_raw(raw, validate=validate)`
   then `collector.finalize(...)` and `return ins` in the `else:` branch.

I am unsure whether the docs example in `docs/metadata.rst` should be updated to show the new
heading; I did not read that section closely enough to claim it is stale, and I am not treating
it as a defect.

## Why it fails

No test fails. All three harness runs are `exit_code=0` with 0 failures. The one thing I had
flagged for checking before writing this report was the removal of `from None` from the old
re-raise; the `__context__` expectations in `tests/test_metadata.py` did not fail in any of the
three runs, so it is not a problem.

## Verdict

VERDICT: approve

## Experience difference

Before this change, `Metadata.from_email()` reported problems in two disconnected ways. A
field the email parser could not read was reported in a group headed `unparsed`, containing
only unreadable lines, e.g. `unrecognized field: 'hello'` or `'name' has invalid data`. Any
other problem - a missing or invalid required field - was reported by a second, separate group
headed `invalid or unparsed metadata`, and the unreadable lines were dropped from that second
group. So one broken file could produce two reports, and a field that was both unreadable and
invalid appeared twice across them, under two different headings.

After the change, there is one report per file, always headed `invalid or unparsed metadata`.
It lists every unreadable line and every missing or invalid required field together, and a
field that is both unreadable and invalid is listed once. Concretely, for the input
`Hello: PyPA` a user now gets a single `ExceptionGroup` with 4 entries - `hello`,
`metadata-version`, `name`, `version` - instead of an unparsed-only group followed by a
required-fields group, which is what `tests/test_metadata.py:364` asserts. For empty input
`""` the group message is `invalid or unparsed metadata` with the three required-field errors
(`tests/test_metadata.py:399`).

Things that did not change: a fully valid file still returns a `Metadata` object with no
exception; `validate=False` still skips the unreadable-line reporting because the loop remains
inside `if validate:`; the wording of the individual errors (`unrecognized field: 'x'` and
`'x' has invalid data`) is unchanged. The docstring at `src/packaging/metadata.py:862-871` and
the `CHANGELOG.rst` entry added under the current release's `Fixes:` section describe the new
single-report behaviour.