# Feedback report

## Tests

The harness ran the project suite (`python -m pytest`) three times. All three
runs exited 0. Quoting the three real summary lines:

- Run 1: `62046 passed, 413 deselected in 141.30s (0:02:21)`
- Run 2: `62046 passed, 413 deselected in 166.93s (0:02:46)`
- Run 3: `62046 passed, 413 deselected in 212.59s (0:03:32)`

Each run collected `62459 items / 413 deselected / 62046 selected`. So: 62046
tests, 62046 passed, 0 failed, in every run. I did not run the tests myself;
these numbers are quoted from the harness output.

## What is missing

I found nothing the ticket asked for that is not implemented.

The ticket asks that a non-string letter in the pre-release slot raise the
usual `InvalidVersion` message instead of escaping as an `AttributeError`, for
both ways of building/swapping a version. Evidence in the code:

- The guard is present in `_validate_pre` at `src/packaging/version.py:290`:
  `if isinstance(letter, str):` wraps `letter = normalize_pre(letter)`.
- Without that guard, baseline `src/packaging/version.py:290` (from
  `git show HEAD:...`) read `letter = normalize_pre(letter)` directly, and
  `normalize_pre` does `letter.lower()` at `src/packaging/version.py:106`, which
  is where a non-string letter produced the `AttributeError`.
- The rejection message is now reached for a bad letter:
  `src/packaging/version.py:295` `msg = f"pre must be a tuple of ('a'|'b'|'rc', non-negative int), got {value}"`
  followed by `raise InvalidVersion(msg)` at line 296.
- Both entry points go through `_validate_pre`: `Version.from_parts` calls it
  at `src/packaging/version.py:494` (`_pre = _validate_pre(pre) if pre is not None else None`)
  and `__replace__` calls it at `src/packaging/version.py:542`
  (`pre = _validate_pre(kwargs["pre"]) if "pre" in kwargs else self._pre`).
  So the one change covers both behaviours the ticket describes.
- The existing test that targets this case is unchanged from baseline:
  `tests/test_version.py:1281-1285`
  `test_from_parts_rejects_non_str_pre_letter` asserts
  `pytest.raises(InvalidVersion, match="pre must be a tuple")` for
  `Version.from_parts(release=(1,), pre=(1, 1))`.

## Why it fails

No test failed. All three harness runs report `62046 passed` and `0 failed`.
I have no failing test to explain.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a product where handing a number to the pre-release letter
slot fails cleanly, and that is what now exists.

Before the change (baseline `src/packaging/version.py:290`), calling
`Version.from_parts(release=(1,), pre=(1, 1))` reached `normalize_pre`, which
calls `letter.lower()` on the integer `1` (`src/packaging/version.py:106`). The
user saw a raw Python `AttributeError` about `'int' object has no attribute
'lower'` — a message that says nothing about versions and does not follow the
`InvalidVersion` contract the rest of the API uses. The same leak applied to
`version.replace(pre=(1, 1))`, because `__replace__` uses the same
`_validate_pre`.

After the change, the same two calls instead raise
`InvalidVersion("pre must be a tuple of ('a'|'b'|'rc', non-negative int), got (1, 1)")`
from `src/packaging/version.py:295-296`. The user gets one consistent error type
and a message that names the expected shape. Valid usage is unchanged: string
letters such as `("a", 1)`, `("A", 0)`, `("Alpha", 2)` and `("bEta", 2)` still
flow through the `isinstance(letter, str)` branch and normalize exactly as
before, so the pre-release strings a correct caller builds are identical to the
old behaviour. The visible difference is limited to the error path: an
unexplained `AttributeError` becomes an actionable `InvalidVersion`. The
harness confirms this with all 62046 tests passing across three runs.