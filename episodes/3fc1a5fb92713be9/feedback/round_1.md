# Feedback report

## Tests

The harness ran the Diff2 suite three times; all three runs are green.

Command: `python -m pytest` (rootdir `/workspace`, `testpaths: tests`).

Run 1 of 3: `exit_code=0`, output ends with
`62103 passed, 417 deselected in 188.06s (0:03:08)` and header
`collected 62520 items / 417 deselected / 62103 selected`.

Run 2 of 3: `exit_code=0`, output ends with
`62103 passed, 417 deselected in 146.99s (0:02:26)`.

Run 3 of 3: `exit_code=0`, output ends with
`62103 passed, 417 deselected in 176.72s (0:02:56)`.

Totals: 62103 selected, 62103 passed, 0 failed, 0 errors (417 deselected) in
each of the three runs. No test was reported as failing.

## What is missing

Nothing. The ticket asks for two things, and both are present in the code I read:

- "The message should repeat my value exactly as I typed it" — the value is
  quoted directly at each message site, e.g. `metadata.py:614`
  `f"{value!r} is invalid for {self.raw_name!r}"` and `metadata.py:626`
  (the version site), `metadata.py:690` (`f"{name!r} is invalid for {self.raw_name!r}"`
  for provides-extra), `metadata.py:700` (requires-python), `metadata.py:713`
  (requires-dist).
- "it should still tell me which field is at fault" — each message also names the
  field via `{self.raw_name!r}` (same lines), so the value and the field name are
  both shown.
- "The old behavior, where my value was re-read as if it were part of the tool's
  own wording, is gone" — `_invalid_metadata` at `metadata.py:593-598` no longer
  calls `format_map`; a grep for `format_map` and `{field}` in
  `src/packaging/metadata.py` returned no matches (the only `field` token left is
  the unrelated loop variable at `metadata.py:830`).

The regression test named in the ticket's hints exists:
`tests/test_metadata.py:501-507` `test_invalid_version_with_placeholder_text`,
asserting at line 507
`assert str(exc_info.value) == "'{field}' is invalid for 'version'"`. This matches
the message produced at `metadata.py:626` and it passed in the harness runs.

## Why it fails

No test fails. All three harness runs reported `0 failed` and `exit_code=0`, so
there is no failure to explain.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a product where, when a metadata value is refused, the error
text repeats exactly what the user typed and separately names the field. Before
the change, a value containing the literal marker `{field}` was re-read through
`format_map`, so that marker was swapped for the field name: typing `{field}` in
the version field produced a message that named the field in place of the value.
The ticket's "User experience" section says this made the message repeat the
field name where the user's value should be, so the user could not see what was
refused.

In the product that exists now, `_invalid_metadata` (`metadata.py:593-598`) builds
`InvalidMetadata(self.raw_name, msg)` with no `format_map`, and every quoting
message is written with a direct f-string that inserts the user value with `!r`
and the field with `{self.raw_name!r}`. So for the exact scenario in the ticket,
typing `{field}` into the version field now gives
`'{field}' is invalid for 'version'` — the value shown unchanged, plus the field
name — which is the behavior the ticket asks for, and this string is asserted at
`tests/test_metadata.py:507` and passed.

The same fix covers the other message areas the ticket lists (name at
`metadata.py:614`, extra names at `metadata.py:690`, required Python version at
`metadata.py:700`, required package lines at `metadata.py:713`), and also the
sibling messages that used the same mechanism (metadata-version at
`metadata.py:603`, license, license-files, import-names at `metadata.py:723-770`).
For values without the marker, the message is unchanged, because the previous
`format_map` with `repr(raw_name)` produced the same text as the new `!r`
insertion. The user-visible difference is limited to values that contain braces:
those are now reported as typed rather than rewritten. No other behavior or
output is affected, and nothing in the ticket's request is left unimplemented.