# Feedback report

## Tests

The pipeline ran the suite 3 times. All 3 runs used the command `python -m pytest`, all exited with code `0`, and all reported the same totals.

Totals (identical in every run): **24 tests collected, 24 passed, 0 failed, 0 errors, 0 skipped.**

Real output excerpt from run 1 of 3:

```
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
plugins: cov-7.1.0
collected 24 items

tests/test_dark_magic.py ....                                            [ 16%]
tests/test_dunders.py ....................                               [100%]

============================== 24 passed in 0.08s ==============================
```

Run 2 of 3 reported `24 passed in 0.10s` and run 3 of 3 reported `24 passed in 0.06s`, with the same per-file breakdown (`tests/test_dark_magic.py ....` and `tests/test_dunders.py ....................`).

The two tests that cover this ticket's feature are both inside that passing set:

- `tests/test_dark_magic.py::TestDarkMagic::test_renaming` — renames a field, calls `C2(x=1, y=2)` and `C2(1, 2)`, and asserts `repr(c)` is `C2(1, 2)`. The positional form only works because the argument name changed, so this test is the direct check of the ticket.
- `tests/test_dunders.py::TestAddInit::test_underscores` — builds a class with `_x` and `_y`, checks the generated script contains `def __init__(self, x, y)`, calls `c = C3(x=1, y=2)`, and asserts `c._x == 1` and `c._y == 2`.

I did not run the tests myself. Every number in this section comes from the harness output above.

## What is missing

Only `attr/_dunders.py` and `docs/examples.rst` are changed (`git status --short` shows `M attr/_dunders.py` and `M docs/examples.rst`). `tests/test_dunders.py` and `tests/test_dark_magic.py` are unchanged from HEAD, so the two tests listed above already existed and act as the acceptance tests for this change.

The behaviour the ticket asks for is implemented. In `attr/_dunders.py` the diff adds `arg_name = a.name.strip("_")` and uses that short name in the generated `__init__` in all four field kinds:

- validator branch, `attr/_dunders.py:187-190` — `def __init__(self, {arg_name}, {a.name}): ...` and `self.{a.name} = {a.name}`
- `default_value` branch, `attr/_dunders.py:191-201` — `def __init__(self, {arg_name}={default_value}): self.{a.name} = {arg_name}`
- `default_factory` branch, `attr/_dunders.py:202-210` — `def __init__(self, {arg_name}=attr.Factory({default_factory})): self.{a.name} = attr.Factory({a.name})`
- plain required field, `attr/_dunders.py:211-216` — `def __init__(self, {arg_name}): self.{a.name} = {arg_name}`

`self.{a.name}` and the `attr_dict['{name}']` key in the generated script keep the full underscored name, and the `__repr__` code path was not touched, so the field is still stored and printed under its full name.

What is thin is test coverage, not the product. The new test uses a single shape: leading underscore only (`_x`, `_y`), no validator, no default. The following cases the ticket mentions are not exercised anywhere in the suite:

- a trailing underscore (the ticket says "leaves a trailing underscore stripped as well")
- a leading and trailing underscore together
- a private field with a validator (the ticket lists this explicitly; the validator test at `tests/test_dunders.py` uses the public name `x`)
- a private field with `default_value` or `default_factory`

`docs/examples.rst` documents the feature with one doctest (`SecretCoordinates(x=1, y=2)` → `SecretCoordinates(_x=1, _y=2)`), which also uses leading underscores only. There is no changelog entry: `docs/changelog.rst` still reads "Initial release" under the `15.0.0 UNRELEASED` heading.

## Why it fails

Nothing fails. All 24 tests passed in all 3 harness runs, with exit code `0` and no errors or skips, so there is no failing test to explain.

## Verdict

VERDICT: approve

## Experience difference

**Before the change.** A field named `_x` produced an `__init__` whose parameter was also named `_x`. The generated line in `attr/_dunders.py` used `a.name` for the parameter, so calling the class meant passing the keyword `C3(_x=1)`. Passing `x=1` raised `TypeError`.

**After the change.** `arg_name = a.name.strip("_")` (`attr/_dunders.py:185`) is used for the parameter in all four field kinds, so the same class is now called as `C3(x=1)`. This is exactly what the ticket asked for, and it is what `tests/test_dunders.py::TestAddInit::test_underscores` asserts.

What stays the same, per the ticket's "nothing was taken away" and confirmed by the code:

- The attribute is still stored under the full name. `self.{a.name}` is unchanged in every branch, so `c._x` still reads and writes, and `tests/test_dunders.py` asserts `c._x == 1`.
- The `repr` is unchanged. `__repr__` was not modified in the diff, and `tests/test_dark_magic.py::test_renaming` asserts `repr(c) == "C2(1, 2)"`.
- Names without underscores are not affected. `strip("_")` returns the same string when there is nothing to strip, so public fields behave exactly as before. `test_renaming` covers this with the public names `x` and `y`.
- The behaviour is uniform across field kinds. The short name is applied to plain fields, fields with a validator, fields with `default_value`, and fields with `default_factory`, so the caller does not have to learn a different rule per field type.

Real differences a user will notice:

- Keyword call style changes. Code that called `C3(_x=1)` must now call `C3(x=1)`. This is the requested change, but it is still a break for callers, and there is no note about it in `docs/changelog.rst`.
- The error message on a wrong keyword is now the short one, so a mistake shows `TypeError: __init__() got an unexpected keyword argument 'x'` for an underscore field, which points at the new name rather than the attribute name.

Areas where a user could hit behaviour that the ticket describes but the suite does not prove, and which I could not confirm by running anything in this round:

- Trailing and leading+trailing underscore names. The code path is the same single `strip("_")` call, so the short name should be produced, but no test or doctest shows it.
- Private fields with a validator, `default_value`, or `default_factory`. All three branches were edited to use `arg_name`, but the existing tests for those branches all use public names, so the edited lines are not covered by a passing test.
- A field made only of underscores, and a class holding both `x` and `_x`. I did not check `attr/_make.py` for any guard against these, so I am not reporting them as defects; they are simply unchecked by the suite.
