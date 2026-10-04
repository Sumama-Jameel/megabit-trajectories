# Feedback report

## Tests

Command run three times from `/workspace`:

```
python3 -m pytest -q
```

- Run 1: `23 passed in 0.07s`
- Run 2: `23 passed in 0.05s`
- Run 3: `23 passed in 0.09s`

Total: 23 tests. Passed: 23. Failed: 0. The result was the same in all three runs.

No install was needed. `python3 -c "import pytest"` reported `pytest 9.1.1 3.11.16` and `import attr` resolved to `/workspace/attr/__init__.py`, so the run used the workspace copy of the library.

The two tests that cover the changed behaviour are:

- `tests/test_dunders.py:160` — `"C(a=1, b=2)" == repr(ReprC(1, 2))`
- `tests/test_make.py:89` — `"C3()" == repr(C3())`

Both passed in all three runs.

## What is missing

Nothing product-wise. The ticket asked for the repr of an attrs class to stop using the bracketed form and to become `C(x=1, y=2)`. That is done in one place, `attr/_dunders.py:114`, which now builds `"{0}({1})".format(...)` instead of `"<{0}({1})>".format(...)`. This is the only spot that adds the brackets.

The docs asked for are also done. Updated in the diff: `README.rst` (the front-page `<C(x=1, y=2)>` and `<C(x=42, y=[])>` examples), `docs/why.rst` lines 16, 23, 117 and the hand-written comparison block at line 129 with its output at line 171, plus a new changelog entry.

`tests/` was not changed. This is correct, not a gap. `git diff HEAD --stat` lists only `attr/_dunders.py`, `README.rst`, `docs/why.rst`, `docs/changelog.rst`. The two hint test files already asserted the plain form at HEAD, so they needed no edit.

Two small housekeeping items only, neither is a behaviour problem:

- The new changelog note is appended as another bullet under the existing `- Initial release.` line in `docs/changelog.rst` (lines 19-25). A reader of the 15.0.0 release notes sees "Initial release." and then a repr-format change side by side with no separate heading. It also uses `--` at line 24 as an em-dash stand-in, while the rest of the file uses real Unicode freely.
- `git status --porcelain` shows untracked `.venv/` and `.megabit_tmp/`. These are local build artifacts and should not be swept into a commit.

## Why it fails

Nothing fails. All 23 tests passed in all three runs, so there is no failing test to explain.

The behaviour the ticket asked for is pinned by tests that already existed and that were not weakened: `tests/test_dunders.py:160` and `tests/test_make.py:89` both assert the bracketed form is gone. Had the change been wrong, or had the brackets still been emitted, those two tests would have failed.

## Verdict

VERDICT: approve

## Experience difference

The only user-visible change is that every generated repr loses its surrounding angle brackets.

- Before, a class with attributes printed `<C(x=1, y=2)>`; now it prints `C(x=1, y=2)`.
- An empty class printed `<C3()>`; now it prints `C3()`. The empty case goes through the same code path in `_add_repr`, since the join over no arguments yields an empty string, and `test_make.py:89` confirms it.
- The inner text is unchanged. Attribute names, values, and their order are the same, so `C(a=1, b=2)` still reads exactly as before, minus the brackets.
- Nothing else moved. `__eq__`, `__hash__`, ordering, and `__init__` are untouched, and `_add_repr`'s signature and behaviour are unchanged. No API was added or removed, and no new import or public name was introduced.

For someone reading the README or `docs/why.rst`, the examples now match what the library actually prints, which is the point of the ticket. The hand-written class-versus-generated comparison at `docs/why.rst:129` and its output at line 171 both lost the brackets, so that block stays self-consistent.

For anyone depending on the old string, this is a visible break: saved output, documentation snippets, log lines being matched on, and user-written tests that hardcode `<C(x=1, y=2)>` all have to be updated. The changelog entry records this as a backwards-incompatible change under 15.0.0, which is the right place for it.

The result matches the product the ticket describes: the library no longer produces the bracketed form at all, and only the intentional mention inside the changelog note still contains it.
