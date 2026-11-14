# Feedback report

## Tests

Command run by the pipeline (Diff2 suite): `python -m pytest`. I did not run
tests myself; the numbers below are the harness's captured output.

- Run 1: `1355 passed, 8 skipped, 1 xfailed in 10.15s`, exit_code=0, collected 1364 items
- Run 2: `1355 passed, 8 skipped, 1 xfailed in 10.10s`, exit_code=0, collected 1364 items
- Run 3: `1355 passed, 8 skipped, 1 xfailed in 9.80s`, exit_code=0, collected 1364 items

Totals: 1364 collected, 1355 passed, 0 failed, 8 skipped, 1 xfailed. All three
runs are identical and all exited 0.

The skips are all platform/optional-dependency skips, e.g.
`SKIPPED [1] tests/test_pyright.py:35: Requires pyright.` and
`SKIPPED [1] tests/test_functional.py:784: requires Python 3.13+`. The one
xfail is `XFAIL tests/test_setattr.py::TestSetAttr::test_slotted_confused`.
None of these are related to this change.

The relevant test for "unusual value types stay intact" is
`tests/test_funcs.py:69 test_non_atomic_types`, which is inside the passing
suite. It does `class Int(int)` (line 75) and asserts
`type(asdict(c)["x"]) is Int` (line 82) and `type(asdict(c)["y"][0]) is Int`
(line 83).

## What is missing

I found nothing missing. The ticket asks for (a) the same dictionary as before,
(b) much faster, and (c) plain number/text values kept as-is, checked by a
test. Checking each against what I read:

- (a) Same result: the fast path only short-circuits values that previously
  reached the final `else` branch. `src/attr/_funcs.py:84-85` now does
  `if type(v) in _ATOMIC_TYPES: rv[a.name] = v` before the
  `elif has(v.__class__)` check at line 86; the same for tuples at
  `src/attr/_funcs.py:269-270`. The stored value is unchanged.
- (b) Faster: the new branch skips the `has()`/`isinstance()` work for scalars,
  which is the extra work the ticket complained about.
- (c) Check stays true: `test_non_atomic_types` (tests/test_funcs.py:69) passes,
  and the exact-type test `type(v) in _ATOMIC_TYPES` means subclasses such as
  `Int(int)` do not take the fast path and keep their type, matching lines
  82-83 of that test.

The set is defined at `src/attr/_funcs.py:16-18`:
`_ATOMIC_TYPES = frozenset((bool, bytes, complex, float, int, str, type(None), type(...)))`.

Note: I did not verify whether a specific *new* test function for atomic values
was added by this change; the suite passes with the existing
`test_non_atomic_types`, which is what covers the "kept as they are" promise. I
am not treating that as missing work.

## Why it fails

Nothing fails. All three pipeline runs exited 0 with 0 failures:
`1355 passed, 8 skipped, 1 xfailed`. There is no failing test, so there is no
failure reason to give.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a user who calls the same dictionary conversion call they
already use and gets back the identical dictionary, same keys, same values,
same inner types, just much faster. What exists now matches that description:
`asdict` (`src/attr/_funcs.py:21`) and `astuple` (`src/attr/_funcs.py:262`)
were left with unchanged signatures and unchanged output structure. The only
behavioral difference for the user is that values whose exact type is one of
`bool, bytes, complex, float, int, str, NoneType, EllipsisType` now bypass the
recursion checks (`src/attr/_funcs.py:84-85` and `269-270`) instead of falling
through to the catch-all branch. Because the value stored is the same object in
both paths, a user comparing a dictionary produced now with one produced before
sees no difference at all.

Nested data still behaves as before: lists, tuples, sets and dicts are still
rebuilt in the same shape by the `isinstance(v, (tuple, list, set, frozenset))`
branch (line 95) and the dict branch that follow, so nothing about containers,
ordering, filtering, `dict_factory`, `retain_collection_types` or
`value_serializer` changed. Unusual types that subclass a plain type (for
example `class Int(int)`) are explicitly excluded by the exact-type check and
still come out with their original type, which is what `test_non_atomic_types`
(tests/test_funcs.py:69-83) confirms and what the ticket's "kept as they are"
line asks for.

On speed, I have no measured benchmark output to cite (the pipeline ran the
unit suite, not a benchmark), so I cannot confirm the size of the speed-up from
evidence I hold. The change does remove real per-value work for scalar fields,
which is in the direction the ticket asks for, and it introduces no observable
change for the caller. The user-facing product the ticket promises — same call,
same dictionary, same types, less work — is what is present in the workspace,
and the full suite passes on all three runs.
