# Feedback report

## Tests

I did not run any tests myself. The numbers below are the harness-owned
Diff2 results handed to me for this workspace.

Command: `python -m pytest` (3 runs, all identical)

- Run 1: `exit_code=0`, 8 tests collected, **8 passed, 0 failed**
- Run 2: `exit_code=0`, 8 tests collected, **8 passed, 0 failed**
- Run 3: `exit_code=0`, 8 tests collected, **8 passed, 0 failed**

Real output excerpt (identical in all three runs):

```
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
plugins: cov-7.1.0
collected 8 items

tests/test_funcs.py ........                                             [100%]

============================== 8 passed in 0.02s ===============================
```

So: **8 total, 8 passed, 0 failed, across 3 identical runs.**

What those 8 tests cover, read from `/workspace/tests/test_funcs.py`:
`TestLs.test_instance` (25), `TestLs.test_handler_non_attrs_class` (33),
`TestLs.test_ls` (43), `TestToDict.test_shallow` (54),
`TestToDict.test_recurse` (63), `TestHas.test_positive` (80),
`TestHas.test_positive_empty` (86), `TestHas.test_negative` (96).

Important: `python -m pytest` does **not** collect doctests. Every new
`.. doctest::` block in `attr/_funcs.py`, `attr/_make.py` and `docs/api.rst`
was not executed by any of the three runs. The only place they run is
`tox -e docs` (`sphinx-build -W -b doctest`, `tox.ini`), which is not in
`envlist = py26, py27, py33, py34, pypy, flake8, manifest`. I checked those
doctests by reading them against the code instead of running them — details
in "Experience difference".

## What is missing

Nothing from the ticket's "What changed" list is absent. Checked one by one
against the source:

- `ls` refuses objects — present, `attr/_funcs.py:33-34`.
- Separate error for a class with no fields — present, `attr/_funcs.py:36-39`
  (`ValueError`), distinct from the `TypeError` at line 34.
- `has` documented for classes and following the same rule — present,
  `attr/_funcs.py:86-110`; it calls `ls` and catches only `ValueError`
  (line 107), so an instance falls through to the `TypeError`.
- `to_dict` recursion — present, `attr/_funcs.py:79-80`.
- `Attribute` exported from the top-level package — present,
  `attr/__init__.py:12` and listed in `__all__` at `attr/__init__.py:24`.
- Written docs for helpers, arguments, switches, returned fields, and a full
  `docs/api.rst` — present, 53 lines added to `docs/api.rst`; `:param`/
  `:return`/`:raises` blocks added in `attr/_funcs.py`, `attr/_make.py`
  (`_make_attr` 96-133, `_add_methods` 158-179, `Attribute` 15-47).

Gaps that are real but not ticket violations:

1. **No test for the `has`-on-instance change.** `has(C(1, 2))` now raises
   `TypeError` instead of returning `True` (`attr/_funcs.py:105-108`). This is
   a behaviour change for existing callers and nothing in
   `tests/test_funcs.py` pins it. `TestHas` (lines 76-100) only covers a
   decorated class, a decorated class with no attributes, and `object`.
2. **No test for the new public export.** `attr.Attribute` being reachable
   from the top level is untested; `tests/test_funcs.py:8-12` still imports it
   from the private `attr._make`, which is exactly the reaching-in the ticket
   wanted to remove.
3. **No test for `to_dict` on a non-attrs object**, and no test deeper than one
   nesting level (`TestToDict.test_recurse`, line 63).
4. **Doctests are unverified by the suite.** The ticket asks for "runnable
   examples"; nothing that actually ran in this workspace executed them.
5. **`attr.NOTHING` was added to `__all__`** (`attr/__init__.py:5,24`) beyond
   the ticket's scope. It is needed by the `docs/api.rst:41-57` example, so it
   is justified, but it is extra public API.
6. `to_dict` documents no `:raises:` (`attr/_funcs.py:43-74`) even though it
   calls `ls` at line 75 and can raise both `ValueError` and `TypeError`.

## Why it fails

**Nothing fails.** All 3 runs were `exit_code=0` with 8/8 passing, so there is
no failing test and no failing-test cause to report. The items in "What is
missing" are coverage and documentation gaps, not test failures.

The one thing I checked manually because the suite does not cover it: the new
`attr.ls` doctest at `attr/_funcs.py:29-31` claims

```
>>> attr.ls(C)
[Attribute(name='x', default_value=NOTHING, default_factory=NOTHING), \
Attribute(name='y', default_value=NOTHING, default_factory=NOTHING)]
```

`Attribute` has no hand-written `__repr__`, but `attr/_make.py:75` does
`Attribute = _add_cmp(_add_repr(Attribute, attrs=_a), attrs=_a)`, and
`_add_repr` (`attr/_dunders.py:110-118`) formats as
`ClassName(field=value, ...)`. Combined with `_Nothing.__repr__` returning
`"NOTHING"` (`attr/_dunders.py:136-137`), the expected output matches. I found
no incorrect doctest by reading. It remains unexecuted.

## Verdict

VERDICT: approve

## Experience difference

**Errors from `ls` — the main ticket item — works as asked.**
`attr/_funcs.py:33-34` raises `TypeError("Passed object must be a class.")` for
anything that is not a `type`; lines 36-39 raise
`ValueError("<class ...> is not an attrs-decorated class.")` for a class with no
`__attrs_attrs__`. Before, passing an instance silently answered for the
instance's class, so a caller mistake produced results about the wrong object;
now it stops with a message that names the problem. The two failure modes are
distinguishable by exception type, which is what the ticket asked for.

**`has` — documented, and stricter.** `attr/_funcs.py:90` says "no instances are
accepted", line 93 declares `:raises TypeError:`, and the doctest at 95-103
shows only the two class cases. In practice `has(C)` is `True`,
`has(D)` on a decorated empty class is `True`, `has(object)` is `False`, and
`has(C(1, 2))` raises `TypeError`. The user-facing change is that a yes/no
question asked with the wrong kind of object now raises instead of answering;
the old lenient answer is gone. Untested, so nothing stops a regression here.

**`to_dict` — nested dicts work; the error message points at the class.**
`attr/_funcs.py:79-80` recurses when a value carries `__attrs_attrs__` and
`recurse is True`, so `to_dict(C(C(1,2), C(3,4)))` gives
`{'x': {'x': 1, 'y': 2}, 'y': {'x': 3, 'y': 4}}` — confirmed by
`TestToDict.test_recurse`. `recurse=False` keeps nested instances as objects.
Because line 75 calls `ls(i.__class__)`, a non-attrs argument produces
`"<class 'str'> is not an attrs-decorated class."` — the message names the
*class* of the object the caller passed, not the object, which is a small
readability wrinkle when debugging a bad `to_dict` call.

**The documentation page is no longer empty.** `docs/api.rst` grew from a bare
title to a contents-indexed page with `autofunction` for `attr.s`, `attr.ib`,
`attr.ls`, `attr.to_dict`, `attr.has`, an `autoclass` for `attr.Attribute`
exposing `from_counting_attr`, and a `.. data::` entry for `attr.NOTHING`
(lines 17-57). `docs/conf.py` adds `doctest_global_setup = 'import attr'`
(line 114) so the `attr.`-qualified examples in the docstrings resolve.
Where a user previously had to read `_funcs.py` to learn that `ls` takes a
class or that `to_dict` takes an instance, the rendered page states it.

**Arguments, switches and returned fields are now written down.** `_make_attr`
documents `default_value` and `default_factory` and the `ValueError` for
setting both (`attr/_make.py:96-133`); `_add_methods` documents all four
switches `add_repr`/`add_cmp`/`add_hash`/`add_init` (`attr/_make.py:158-179`);
`Attribute` documents `name`, `default_value` and `default_factory` as
`:ivar:` fields and warns against instantiating it (`attr/_make.py:15-47`).
That covers the ticket's "every helper, argument, switch, and returned field".

**Two documentation risks I could not settle by running anything.** First, the
new docstrings use many single-backtick default-role references (`` `True` ``,
`` `attr.Attribute.default_value` ``) while `default_role` is still commented
out at `docs/conf.py:118`, and `tox -e docs` runs `sphinx-build -W`. If Sphinx
emits an error-level warning per unresolved default role, that build fails —
unverifiable here because the harness only ran `python -m pytest`. Second,
`docs/api.rst:60` documents `_CountingAttr` as a parameter type while the class
is private and appears nowhere in the reference. Neither affects the 8 passing
tests; both would surface the first time someone runs the docs environment.

**Net:** the two user-visible errors from the ticket behave as described, the
yes/no check and the nested-dict conversion work, `attr.Attribute` is reachable
from the top level, and the reference page exists with per-argument prose and
runnable examples. What is missing is proof, not function: no test pins the
`has`-on-instance behaviour, none pins the new export, and none of the new
doctests were executed by any of the three verified runs.