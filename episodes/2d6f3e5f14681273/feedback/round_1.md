# Feedback report

## Tests

I did not run the tests. The pipeline ran them and gave me the results, which I quote here.

Command: `python -m pytest` (rootdir `/workspace`, configfile `pyproject.toml`, testpaths `tests`).

- Collected: 1365 items.
- Result on all three runs: `1356 passed, 8 skipped, 1 xfailed`.
- Failures: 0.
- Exit code: 0 on all three runs (`exit_code=0 classification=substantive`).
- Run 1: `1356 passed, 8 skipped, 1 xfailed in 27.04s`.
- Run 2: `1356 passed, 8 skipped, 1 xfailed in 25.99s`.
- Run 3: `1356 passed, 8 skipped, 1 xfailed in 26.58s`.

The 8 skips and 1 xfail are environment/out-of-scope markers, not new failures. From the harness output: `SKIPPED [1] tests/test_functional.py:784: requires Python 3.13+`, `SKIPPED [1] tests/test_functional.py:798: requires Python 3.13+`, `SKIPPED [1] tests/test_make.py:2834: Pre-3.10 only.`, three `tests/test_pyright.py` skips with reason `Requires pyright.`, `SKIPPED [1] tests/test_slots.py:503: slots without weakref_slot should only work on PyPy`, and `XFAIL tests/test_setattr.py::TestSetAttr::test_slotted_confused`.

## What is missing

Nothing on the evidence I read. The ticket asks for one thing only: `astuple` should "spot plain values early, the same way the dictionary helper already does", with "the choice for how collections are handled stay[ing] the same" and the result unchanged.

The change does exactly that. The staged diff in `src/attr/_funcs.py` is:

```
-            if has(v.__class__):
+            if v.__class__ in _ATOMIC_TYPES:
+                rv.append(v)
+            elif has(v.__class__):
```

`_ATOMIC_TYPES` is a module-level frozenset already used by `asdict` and `_asdict_anything` in the same file, and the new branch is the plain-value short-circuit the ticket describes.

I am not listing these as missing, because the ticket did not ask for them:
- no `changelog.d` fragment for this change (the project has that convention, e.g. `changelog.d/1463.change.md` for the comparable `asdict` speedup, but the ticket does not request a fragment);
- no new test in `tests/test_funcs.py` (the ticket points there only as a hint; the existing `TestAsTuple` coverage already exercises the branch);
- no benchmark assertion (`bench/test_benchmarks.py` entries are timing-only, not pass/fail gates).

One honest uncertainty, kept as a note and not a blocking item: the speedup itself is not numerically proven by any assertion in the suite. What the suite proves is that behaviour is unchanged; the faster path is verified by reading the code, not by a measured number. That is a measurement gap, not a defect.

## Why it fails

No test failed. `1356 passed, 8 skipped, 1 xfailed`, exit code 0, on all three runs, so there is no failing test to explain.

By reading the code, the new branch preserves behaviour: for an exact atomic type the old code already fell through the `has()`/isinstance checks to `rv.append(v)` at the end of the loop, so appending `v` directly reaches the same result with the same value, order and type. Subclasses of atomics are not members of the frozenset, so they still take the old path; the existing `test_non_atomic_types` case in `tests/test_funcs.py` asserts `type(result[0]) is Int` and it passed. The collection, dict, `retain_collection_types` and `tuple_factory` paths are untouched, so the "collections behave the same" part holds.

## Verdict

VERDICT: approve

## Experience difference

The product the ticket describes is the product that exists now, with one internal difference that a user feels as speed rather than as a new feature.

Before this change, a user looping over many `attrs` objects calling `astuple` on each one paid the full check chain on every plain scalar inside the object: each `int`, `str`, `bool`, `float`, `bytes`, `None`, `complex`, `range`, `type`, `property` or `Ellipsis` value went through the `has()` and `isinstance` dispatch before it was finally appended as-is. That work repeated for every scalar of every object in the loop.

After this change, those exact plain values are recognised at the top of the loop by `v.__class__ in _ATOMIC_TYPES` and are appended straight away, skipping the dispatch, while the loop keeps checking everything else the same way it did before.

What the user sees is unchanged in every observable respect: `astuple` returns the same tuples, with the same values in the same order, of the same types; the `filter` behaviour is the same; recursion into nested structures is the same; custom subclasses of the atomic types are still treated the way they were and are not flattened; and the options that control collection handling (`tuple_factory`, `retain_collection_types`) keep the same effect as before, because those code paths are untouched and the whole suite (1356 tests) passes. Nothing new is exposed through the public API and no signature, docstring-visible behaviour or error path changes. The net user-visible difference is only that the same tuples come back sooner for objects that carry many plain scalar fields.