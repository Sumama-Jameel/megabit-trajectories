# Feedback report

## Tests

The pipeline ran the Diff2 suite for this workspace. I did not run any tests myself and I installed nothing.

Command: `python -m pytest`, run 3 times (runs 1, 2 and 3 all identical in result).

- Total collected: 60
- Passed: 60
- Failed: 0
- Errors: 0
- Exit code: 0 (all 3 runs, `classification=substantive`)

Real output excerpt (run 1 of 3):

```
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
plugins: cov-7.1.0
collected 60 items

tests/test_dark_magic.py ....                                            [  6%]
tests/test_dunders.py .......................                            [ 45%]
tests/test_funcs.py .........                                            [ 60%]
tests/test_make.py ..................                                    [ 90%]
tests/test_validators.py ......                                          [100%]

============================== 60 passed in 0.09s ==============================
```

Per-file breakdown: `test_dark_magic.py` 4, `test_dunders.py` 23, `test_funcs.py` 9, `test_make.py` 18, `test_validators.py` 6.

## What is missing

The ticket asked for a naming-only change: write the two main public names the public way *everywhere inside the project* — "in the class-building module, in the checks module, and in the project's own test files" — and "no name a user relies on disappears."

Checked against the staged diff (3 files, +24/-14: `attr/__init__.py`, `attr/_make.py`, `attr/validators.py`):

- Class-building module — done. The public definitions are now `ib` and `attributes`; the two old private names survive only as assignment aliases at `attr/_make.py:113` (`_make_attr = ib`) and `attr/_make.py:190` (`_add_methods = attributes`).
- Checks module — done. `attr/validators.py` now uses `@attributes(add_repr=False)` (lines 48, 53) and `ib()` (lines 5, 10) instead of the private spellings.
- Test files — already correct before this change. `git show HEAD:tests/test_make.py` already imported `attributes` and `attr` from `attr._make`, and `tests/test_funcs.py:12-16` already used `attributes`/`attr`. Nothing in `tests/` referenced the private names, so no test edit was needed to satisfy this clause.
- Nothing a user relies on disappeared. `attr/__init__.py:26-27` still exports `attr = ib` and `s = attributes`; `__all__` is unchanged and still lists `Attribute, NOTHING, attr, attributes, has, ib, ls, s, to_dict, validators`.
- A whole-tree `grep` for `_make_attr|_add_methods` returns only the two deliberate back-compat aliases at `attr/_make.py:113` and `attr/_make.py:190`. Tests, docs and `README.rst` have zero private references. `attr/_funcs.py` contains no import of these names at all, so it was never a gap.
- Docs: `docs/api.rst` autodocs the public names (`automodule:: attr`, `autofunction:: ib`, `autoclass:: attributes`, `s`, `attr`), so the docs words now match the shipped code as the ticket asked.

Two small observations, neither blocking and neither a ticket requirement:

- `docs/changelog.rst` was not touched; under 15.0.0 it still shows only "Initial release". The change is naming-only and not user-visible, so this is a judgement call, not a gap.
- In `attr/_make.py` the module-level public alias `attr` coexists with a local generator variable also named `attr` at `attr/_make.py:123`. Nothing is broken today, but inside that function the bare word `attr` now reads ambiguously.

## Why it fails

Nothing fails. All 60 tests passed in all 3 runs with exit code 0, so there are no failing tests to explain.

## Verdict

VERDICT: approve

## Experience difference

Ticket as described vs. what exists now:

- Reading the code. Before, someone opening `attr/_make.py` saw the real definitions named `_make_attr` and `_add_methods` and had to remember that the public names were just aliases pointing at them. Now the definitions carry the public names `ib` (`attr/_make.py:110`) and `attributes` (`attr/_make.py:187`), and the private names point the other way. Someone reading top to bottom sees the same words the docs use.
- Writing validators. A contributor adding a new validator no longer types a private-sounding `@_add_methods(add_repr=False)` and `_make_attr()`; they type the public `@attributes(add_repr=False)` and `ib()`, matching every example in `docs/api.rst`.
- Following a doc example. The docs advertise `attr.s`, `attr.attributes`, `attr.ib` and `attr.attr`; before this change the shipped implementation of two of those was spelled differently internally. Now the code matches the docs word for word, so copy-paste from `README.rst` and `docs/examples.rst` lands on names that are literally what is defined.
- Using the library. No difference, by design and by evidence. `attr.attr`, `attr.s`, `attr.ib`, `attr.attributes` all still import and work; `__all__` is unchanged; the private spellings remain importable from `attr._make` for anyone who reached for them. Nothing a user relies on was removed.
- Running the tests. No difference: 60 tests, same set of files, all green. The rename touched no test file because the tests were already written against the public names, which is what made the mismatch a pure naming inconsistency rather than a behaviour risk.
- What a user cannot tell. The change is deliberately invisible from outside the package apart from introspection: there is no new feature, no new keyword, no new error message, and no changed output. `docs/changelog.rst` not listing it is consistent with that.
