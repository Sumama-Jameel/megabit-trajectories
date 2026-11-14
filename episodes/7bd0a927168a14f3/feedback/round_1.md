# Feedback report

## Tests

I did not run the tests myself. The pipeline ran the Diff2 suite for this workspace and the results below are quoted from that harness output.

Command (harness, 3 runs): `python -m pytest` (rootdir `/workspace`, Python 3.11.16, pytest-9.1.1, pluggy-1.6.0, plugin `cov-7.1.0`).

- Total tests: **33**
- Passed: **33**
- Failed: **0**
- Errors: **0**
- Exit code: **0** in all 3 runs
- Classification on all 3 runs: `substantive`

Real output excerpt, identical in runs 1, 2 and 3:

```
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
plugins: cov-7.1.0
collected 33 items

tests/test_dark_magic.py ..                                              [  6%]
tests/test_dunders.py .................                                  [ 57%]
tests/test_funcs.py ........                                             [ 81%]
tests/test_make.py ......                                                [100%]

============================== 33 passed in 0.05s ==============================
```

The 8 tests in `tests/test_funcs.py` include the three that cover the ticket: `TestHas::test_positive` (`tests/test_funcs.py:79`), `TestHas::test_positive_empty` (`tests/test_funcs.py:85`) and `TestHas::test_negative` (`tests/test_funcs.py:95`). Those tests are byte-identical to HEAD (verified with `git show HEAD:tests/test_funcs.py`), i.e. the suite already shipped the expectations and the change only had to satisfy them.

Not covered by the run: the doctest lines inside the new `has` docstring (`attr/_funcs.py:26-33`) were **not** collected. The harness command has no `--doctest-modules` and the session header shows no doctest plugin, so those example lines are unverified by the suite. Same for the pre-existing `ls` docstring examples.

## What is missing

Product-wise, nothing from the ticket is missing. Each asked-for behaviour is implemented and reachable:

- `has()` exists in `/workspace/attr/_funcs.py` (lines 20-35), right after `ls` and the other helpers.
- It is exported as public API: `attr/__init__.py` lines 6-9 import it and `__all__` at `attr/__init__.py:22` lists `"has"`.
- A decorated class with fields returns `True`; a decorated class with no fields returns `True`; a plain `object` returns `False`. All three are asserted by the passing tests above.

What is genuinely absent, neither of which the ticket requires:

- `docs/api.rst` is 4 lines (a title and nothing else). A grep for `has`, `ls(` and `to_dict` across `/workspace/docs` returned no match, so the new public function is not described anywhere in the docs. A user reading the docs cannot learn that `has` exists.
- `docs/changelog.rst` was not touched, so there is no note that `attr.has` was added.

Neither is a blocker. They are the normal follow-up a maintainer would want for a new public name.

## Why it fails

Nothing fails. 0 of 33 tests failed, so there is no failing test to explain.

The three ticket requirements each match the code, which is why the suite is green:

- Decorated class with fields: the class `C` at `tests/test_funcs.py:15-17` is decorated, so the `s` decorator stored its attribute tuple on the class; `has` finds it and returns `True`.
- Decorated class with no fields: `s` always assigns `cl.__attrs_attrs__ = []` (`attr/_make.py:99`), and `has` tests `is not None` (`attr/_funcs.py:35`) rather than truthiness. An empty list is falsy but is not `None`, so `has` correctly returns `True` instead of `False`. Using `if getattr(...)` here would have been the bug, and the implementation avoids it.
- Plain `object`: `object` has no `__attrs_attrs__`, `getattr` returns the `None` default, so `has` returns `False`.

## Verdict

VERDICT: approve

## Experience difference

What the ticket asks for versus what exists now, in user terms.

Before the change, the only membership test available was `ls` (`attr/_funcs.py:10-17`). It coerces the argument to a class and, when the class is not an attrs class, raises `TypeError` with a formatted message naming the type. So every "is this an attrs class?" question had to be written as a `try/except` block, and the answer was an exception rather than a value.

After the change, a user writes `attr.has(C)` and gets a plain `True`/`False` back. It never raises for any input, so a caller can branch directly: check `has` first, then call `ls` only when it is `True`. This removes the control-flow-by-exception pattern from user code and is the practical reason the ticket asked for the function.

The implementation is a single `getattr(cl, "__attrs_attrs__", None) is not None` check (`attr/_funcs.py:35`). It is cheap, it reads the same marker that `ls` and the rest of the library already use, and it accepts a class exactly as the ticket specified.

Three honest limits a user would feel, none of them a defect against this ticket:

- `has` does not coerce. It looks up the marker on whatever it is given. `ls(C(1, 2))` answers for the class `C`, but `has(C(1, 2))` looks at the instance and returns `False`. A user who reaches for `has` out of habit after using `ls` gets a quiet wrong answer rather than an error. The ticket only asked for classes, so this is not a gap in the work, but it is a real difference between the two functions.
- `has` is an attribute lookup, so it inherits normal lookup rules. A subclass of an attrs class, or any class that copies `__attrs_attrs__`, reports `True` even if nothing was generated for it. `has` answers "does this object carry the attrs marker", not "was this class processed by attrs".
- The new function is public (`__all__` at `attr/__init__.py:22`) but undocumented, because `docs/api.rst` has no entry for it. The discoverable path is the source or the changelog, and the changelog was not updated either.

Finally, the examples written in the new docstring (`attr/_funcs.py:26-33`) are a real part of what a user reads, and the suite did not execute them. They should be treated as unverified until doctests are run.

VERDICT: approve
