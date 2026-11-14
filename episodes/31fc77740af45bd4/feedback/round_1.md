# Feedback report

## Tests

The pipeline ran the project's suite three times. I did not run tests myself and I did not
install anything this round.

Command: `python -m pytest` (rootdir `/workspace`, configfile `pyproject.toml`, testpaths `tests`).

Every one of the three runs reported the same result:

```
collected 1386 items
================= 1377 passed, 8 skipped, 1 xfailed in 33.61s ==================
```

Run 1: 1377 passed, 8 skipped, 1 xfailed, 0 failed (33.61s), exit_code=0.
Run 2: 1377 passed, 8 skipped, 1 xfailed, 0 failed (32.52s), exit_code=0.
Run 3: 1377 passed, 8 skipped, 1 xfailed, 0 failed (33.09s), exit_code=0.

Totals across the three runs: 4158 collected, 4131 passed, 24 skipped, 3 xfailed, **0 failed**.

Skips are all pre-existing/environmental, per the captured output:
`tests/test_functional.py:795` and `:809` "requires Python 3.13+",
`tests/test_make.py:3029` "Pre-3.10 only.",
`tests/test_pyright.py:35`, `:83`, `:111` "Requires pyright.",
`tests/test_slots.py:517` "slots without weakref_slot should only work on PyPy".
One xfail: `tests/test_setattr.py::TestSetAttr::test_slotted_confused`.

Two things I could not confirm from that output, and I am not claiming them either way:

- The new doctest in `docs/api.rst:161-162` (`>>> attrs.fields(C(1, "test")) is attrs.fields(C)`
  / `True`) is almost certainly **not** part of this run. The captured session shows
  `testpaths: tests` and only `tests/*` files in the progress list, and `pyproject.toml`
  `addopts` carries no `--doctest-modules`/`--doctest-glob`. So the docs example is
  unexecuted here. It is a one-line example consistent with `tests/test_make.py:1550-1565`,
  so I am flagging it as unverified, not as broken.
- The stub change at `src/attr/__init__.pyi:311` is a `.pyi` file, so it is not executed by
  pytest. The mypy fixtures live in `tests/test_mypy.yml` and are driven by a separate
  tox/mypy run, which is not in the captured output. Again: unverified, not failing.

## What is missing

Nothing the ticket asked for is missing. Going item by item against `/megabit/ticket.md`:

1. **Instances accepted by `attrs.fields()`** — implemented at `src/attr/_make.py:1915-1924`:
   when the argument is not a type and has no generic base, it reads
   `getattr(cls, "__attrs_attrs__", None)` and returns it.
2. **`TypeError` names both classes and instances** — implemented at `src/attr/_make.py:1922`:
   `"Passed object must be a class or attrs instance."`
3. **Docs example showing object and class give the same answer** — added at
   `docs/api.rst:161-162`.
4. **Stub widened** — `src/attr/__init__.pyi:311` is now
   `def fields(cls: type[AttrsInstance] | AttrsInstance) -> Any: ...`. The `attrs` namespace
   needs nothing extra: `src/attrs/__init__.pyi:32` re-exports `fields` from `attr`.
5. **Old "instances must be rejected" expectation** — the ticket asks for this expectation to
   be removed. `git diff HEAD --stat -- tests/` is empty, and `tests/test_make.py:1550-1565`
   already asserts `fields(C()) is fields(C)` and already matches
   `r"Passed object must be a class or attrs instance\."`. So the workspace already carries the
   post-change expectations; this diff does not need to delete them, and I am not counting that
   as missing work.
6. **Changelog** — present as `changelog.d/1497.change.md`.

Also updated for consistency: the docstring at `src/attr/_make.py:1902` and a
`.. versionchanged:: 26.2.0` note at `src/attr/_make.py:1913`.

One open question, stated plainly and not treated as a defect: `fields_dict()` is unchanged.
`src/attr/_make.py:1963` still raises `"Passed object must be a class."` for non-class input,
and `tests/test_make.py:1634-1641` still asserts that rejection. The ticket names `attrs.fields()`
in both the title and the "What changed" text, so narrow scope looks intended. I am unsure
whether widening `fields_dict` was also wanted; it is not blocking.

## Why it fails

Nothing fails. Across all three harness runs: 0 failed, 0 errors, exit_code=0. There is no
failing test to explain.

## Verdict

VERDICT: approve

## Experience difference

**Before this change**

- `attrs.fields(x)` where `x` is an instance raised `TypeError: Passed object must be a
  class.` The message named only classes, so a user who passed an instance was told their
  object was not a class and left guessing.
- To get fields for an instance you had to know to reach through to the type yourself,
  e.g. `attrs.fields(type(x))` or `x.__attrs_attrs__`.
- In an editor or type checker, `attrs.fields(some_instance)` was flagged, because the stub
  only accepted `type[AttrsInstance]`.

**After this change**

- `attrs.fields(instance)` returns the field tuple of that instance's class. Because it looks
  up `__attrs_attrs__` on the object, `attrs.fields(C()) is attrs.fields(C)` — same object,
  same result for instance and for class.
- The error for genuinely unusable input is `TypeError: Passed object must be a class or attrs
  instance.`, so the message now names both accepted kinds and a wrong argument is
  self-explanatory. The docstring and a `versionchanged` note say so in the API docs.
- `docs/api.rst:161-162` shows the new behaviour as a runnable example:
  `>>> attrs.fields(C(1, "test")) is attrs.fields(C)` → `True`.
- `src/attr/__init__.pyi:311` accepts `type[AttrsInstance] | AttrsInstance`, so passing an
  instance is no longer a type error, and `attrs.fields` inherits this through the
  `src/attrs/__init__.pyi:32` re-export — both import styles behave the same.
- Behaviour for plain classes, generic aliases and non-attrs objects is untouched: the new
  branch runs only when the argument is not a `type` and no generic base applies. A non-attrs
  instance still raises the same `TypeError`, just with the improved wording.

**What a user still cannot do**

- `attrs.fields_dict(instance)` still raises `TypeError: Passed object must be a class.`
  (`src/attr/_make.py:1963`, asserted by `tests/test_make.py:1634-1641`). The two APIs are now
  inconsistent with each other. If that was not intended, it is a follow-up ticket, not a
  blocker on this one.

**Residual risk**

- The docs example and the `.pyi` stub are the two parts of this change that the captured
  pytest runs did not execute (docs doctests need the sphinx tox env; stubs need the mypy
  run). They are consistent with the passing tests, but nobody has actually run them in this
  round.