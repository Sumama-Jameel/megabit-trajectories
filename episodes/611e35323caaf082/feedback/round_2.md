# Feedback report

## Tests

Environment: `/workspace/.venv` already had the runner, so nothing was installed.
`/workspace/.venv/bin/python -c "import pytest, attr"` -> `pytest ok 9.1.1`.

Command, run three times:

```
cd /workspace && for i in 1 2 3; do .venv/bin/python -m pytest tests -q; done
```

Real output:

```
=========== RUN 1 ===========
.......................                                                  [100%]
23 passed in 0.07s
RUN 1 EXIT: 0
=========== RUN 2 ===========
.......................                                                  [100%]
23 passed in 0.05s
RUN 2 EXIT: 0
=========== RUN 3 ===========
.......................                                                  [100%]
23 passed in 0.09s
RUN 3 EXIT: 0
```

Total: 23 tests collected. 23 passed, 0 failed, 0 skipped in each of the three runs.
Exit code 0 all three times. The result is stable across runs, so nothing here is flaky.

Not run: `flake8 attr tests` and `sphinx-build -b doctest` (both in `tox.ini:17` and
`tox.ini:23`). The change only edits string literals, so flake8 is unaffected, but the
doctest build was not executed and is therefore not verified by this report.

## What is missing

The ticket's product change is fully present. Only documentation hygiene is left.

- `docs/changelog.rst` was not touched. Every attrs class now prints a different
  `repr`, so this is a visible change for anyone whose own tests or saved text
  compare against the old bracketed output. No changelog entry says so. The ticket
  did not ask for one, so this is a minor gap, not a blocker.
- `setup.py:49` still points its test command at `"test_attrs.py"`, a file that does
  not exist. This is pre-existing and unrelated to the change.

Nothing user-facing from the ticket is unimplemented. Both worked examples produce the
exact output the ticket specifies, and the hand-written comparison class was updated
too.

## Why it fails

Nothing fails. 23 passed, 0 failed, on all three runs.

The two tests that cover this ticket are:
- `tests/test_dunders.py:160` — `assert "C(a=1, b=2)" == repr(ReprC(1, 2))`
- `tests/test_make.py:89` — `assert "C3()" == repr(C3())`

Both expect the plain, bracket-free form and both pass. `git show HEAD:tests/test_make.py`
shows these lines unchanged at the base commit, so they were red before the fix and are
the real regression checks for this change.

## Verdict

VERDICT: approve

## Experience difference

Before, `repr(C(1, 2))` printed `<C(x=1, y=2)>` and an empty class printed `<C3()>`.
After the one-line change at `attr/_dunders.py:114`, the same code prints `C(x=1, y=2)`
and `C3()`.

What is unchanged: the field values, their order, the `a=value` formatting, the class
name, and every other dunder (`eq`, `hash`, `init`). The generated `__init__` filename
string at `attr/_dunders.py:151` still reads `<attrs generated init ...>`, correctly
unaffected.

For a reader of `README.rst` and `docs/why.rst`, the shown output now matches what a
REPL or debugger actually prints. That includes the hand-written `ArtisinalClass`
example at `docs/why.rst:129` and its output at `docs/why.rst:171`, so the side-by-side
comparison the guide invites readers to make is now accurate rather than misleading.

A search for leftovers came back clean: `git grep -E "<C|<Class|<C3|\(%s="` over
`attr tests docs README.rst CHANGELOG` returned no matches, and a docs-wide grep for
`<Name(` in `*.rst` found no matches. So the bracketed form is gone from code and prose
alike.
