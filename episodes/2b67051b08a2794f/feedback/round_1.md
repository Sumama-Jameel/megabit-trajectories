# Feedback report

## Tests

I did not run any test command myself. The numbers below come from the pipeline's Diff2 suite, which ran `python -m pytest` in `/workspace` three times. All three runs are identical and exited 0.

Totals from the harness output:

- Collected: 34 tests
- Passed: 34
- Failed: 0
- Errors: 0

Real excerpt (run 1 of 3, `python -m pytest`, `exit_code=0`):

```
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
plugins: cov-7.1.0
collected 34 items

tests/test_dark_magic.py ..                                              [  5%]
tests/test_dunders.py ..................                                 [ 58%]
tests/test_funcs.py ........                                             [ 82%]
tests/test_make.py ......                                                [100%]

============================== 34 passed in 0.07s ==============================
```

Runs 2 and 3 produced the same collection and `34 passed in 0.05s`, `exit_code=0`.

The tests that matter for this ticket are inside that 34:

- `tests/test_dunders.py::TestAddInit::test_validator` (starts at `tests/test_dunders.py:250`) — checks that a failing validator raises `ValueError` from `__init__`, that the message names the offending value, and that an object is not usable after the failure. It is in the passing 18.
- `tests/test_dark_magic.py::TestDarkMagic::test_ls` (`tests/test_dark_magic.py:30`) — checks the `attr.ls` listing, which now includes the validator entry. It is in the passing 2.

Note: `git diff HEAD --stat -- tests/` is empty. The change adds no new tests; the validator tests already sit in the worktree unchanged. The suite passing means the existing expectations still hold, but nothing new was added to pin the new behaviour down.

Also note what was NOT run: the pytest command collects `tests/` only. It does not build the docs, so the new doctest blocks added in `docs/api.rst` were not executed by the harness. `docs/conf.py:61-66` registers `sphinx.ext.doctest`, and `docs/conf.py` sets no `doctest_global_setup`, while `docs/api.rst:14` does `>>> import attr` inside the first example only. The new examples therefore depend on names left over from the earlier block in the same file. This is unverified, not broken — but nobody has proven it.

## What is missing

Product-wise, the ticket asks for four things and I can point at each one in the code:

1. Per-field validators — `attr/_make.py`: `Attribute.__init__` now takes a fourth parameter `validator`; `_CountingAttr.__init__` and `_make_attr` accept `validator=None`; `from_counting_attr` (`attr/_make.py:36-41`) copies `ca.validator` into the real `Attribute`.
2. Validators run inside the generated `__init__` before the value is stored — `attr/_dunders.py:190-196` builds a `validation(value, a=a)` helper; it is wired into the plain branch, the default-value branch, and the factory branch (`attr/_dunders.py:213`, `attr/_dunders.py:217`).
3. The field listing shows the check — `attr/_make.py:45-46` (`Attribute._a`) and `attr/_make.py:52-56` (`_CountingAttr.__attrs_attrs__`) both list `"validator"`, so `attr.ls` prints it. `tests/test_dark_magic.py:30` passes with that new column.
4. The story page uses the current name — `docs/why.rst:189` changed `attrib` to `attrs`. `git grep -n "attrib" HEAD -- docs README.rst` showed that was the only old-name hit outside the word "attribute".

Nothing in the ticket's list is unimplemented. Two gaps remain in evidence, not in code:

- No new tests in the diff. The behaviour is covered only by tests that were already there.
- The doc examples were never executed by the run.

`attr/__init__.py` is unchanged, which is correct: `validator` is a keyword argument on `attr.ib`, not a new exported name, so there was nothing to add there.

## Why it fails

No test fails. 34 of 34 pass in all three harness runs, exit code 0. There is no failing test to explain.

## Verdict

VERDICT: approve

## Experience difference

Before this change, checking an argument meant writing the check by hand and calling it inside a hand-written `__init__`, after the field was already assigned. A bad value was caught late, the half-built object still existed, and the traceback pointed at your own constructor code rather than at the library.

After this change, the check is declared next to the field with `attr.ib(validator=...)`. The generated `__init__` runs it before the value is written to `self`, so a failing check means no object comes back at all — the exception comes straight out of `C(...)`. The three shapes behave the same: a plain argument, an argument with a default, and an argument with a default factory (the factory branch at `attr/_dunders.py:217` validates `self.x` after the factory fills it in, so a factory-produced value is checked too). Fields with no check pay nothing at runtime: the generated line is empty for them and `_dunders.py:224` filters empty lines out of the joined setter block.

The listing changed with it. `attr.ls` now carries a `validator=` entry, showing the callable or `None`, so reading the listing tells you directly which fields are guarded and which are not — a piece of information that was previously invisible and undocumented anywhere in the object itself. `docs/api.rst` was updated to match that output.

The story page reads consistently now: `docs/why.rst:189` uses `attrs` like the rest of the docs, so a reader following the walkthrough no longer sees a module name that does not exist.

Two things a reader should still be told were never checked. The pytest run covers `tests/` only, so the new doctest examples in `docs/api.rst` — the failing-validator example and the updated `attr.ls` output — were never executed by the harness; nothing in this run proves they are accurate. And because the diff contains no new tests, the validator behaviour is pinned down only by pre-existing expectations, which means a future edit could move the behaviour and the suite would not notice as clearly as it could.