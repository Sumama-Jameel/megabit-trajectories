# Feedback report

## Tests

The harness ran the suite 3 times, all runs identical, exit code 0.

Command: `python -m pytest` (run 1, 2 and 3 of 3, all exit_code=0).

Totals from the harness: **8 tests collected, 8 passed, 0 failed, 0 skipped, 0 errors.**

Real output excerpt (identical in all three runs):

```
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
plugins: cov-7.1.0
collected 8 items

tests/test_funcs.py ........                                             [100%]

============================== 8 passed in 0.03s ===============================
```

All 8 tests live in one file, `tests/test_funcs.py` (3 `TestLs`, 2 `TestToDict`, 3 `TestHas`). The other test file, `tests/test_make.py`, was not collected because it does not exist in this workspace.

Note on coverage: this run is plain `python -m pytest`, so **no doctest was executed**. The examples inside the new docstrings were therefore not verified by this run.

## What is missing

**Product-side (from the ticket):**

- The ticket's own hint list names `tests/test_funcs.py`, but that file is **not modified** in this change. The staged diff touches only `attr/__init__.py` (+3/-1), `attr/_funcs.py` (+79/-12), `attr/_make.py` (+88/-1) and `docs/api.rst` (+31). So no test was added for anything the ticket introduced.
- Specifically untested: that `attr.has(C(1, 2))` raises `TypeError` for a non-class, that `attr.ls(C)` keeps definition order and yields `attr.Attribute` instances, and that `attr.Attribute` is importable from the top-level `attr` package (`attr/__init__.py`, which adds `Attribute` to the imports and to `__all__`).
- No test exercises `ls()` with no arguments, or `ls()` on a class whose attributes carry `repr=False`, even though both are documented in the `ls` docstring.

**User-experience-side:**

- The `has()` error message is deliberately different from `ls()`. `ls` raises `ValueError("Passed object must be a class.")`; `has` raises `TypeError("Passed object must be a class.")`. This inconsistency is documented (`attr/_funcs.py`, `has` and `ls` docstrings) but is not tested, so it can silently regress.
- `attr.Attribute` is decorated after the class body with `_add_cmp(_add_repr(Attribute, attrs=_a), attrs=_a)`. In `docs/api.rst` the entry is `.. autoclass:: attr.Attribute` with `:members:`. Because the decorator runs after the class is created, the dunder methods on the public class are the injected `attrs`-generated ones, and the docstring added for the `from_counting_attr` counting-attribute behaviour is not part of the public API page in a form a reader can act on.

## Why it fails

No test failed. All 8 tests passed in all three harness runs.

The open items are things this run **cannot** show, and each one is a gap rather than a red test:

1. `has` raises `TypeError` from an inner `except ValueError`-only guard (`attr/_funcs.py`, body of `has`). Passing an instance therefore surfaces `TypeError("has() argument must be a class.")` rather than a clean `False`. No test asserts this string, so the current pass tells us nothing about it.
2. The `ls` docstring example (`attr/_funcs.py`, `ls` docstring) shows the attributes rendered on one line, but `attr/_dunders.py` `_make_repr` adds no line wrapping — the real `repr()` emits one attribute per line. This example is a `.. code-block:: python` block with a `>>>`, so it is a doctest candidate; `python -m pytest` does not run doctests, so it stayed green. Under a `sphinx-build -b doctest` or `--doctest-modules` run this example would not match actual output.
3. `docs/conf.py` enables `sphinx.ext.doctest`, but there is no `doctest_global_setup` supplying `import attr`, while every example in the new docstrings uses bare `attr.` names (only `docs/api.rst` has an import in its own block). Same conclusion as above: not exercised by `pytest`.
4. The new docstring markup uses single-backtick Sphinx roles (for example the `attr.Attribute` and `attr.Attribute` cross-references in `attr/_funcs.py` and the `:param _CountingAttr ca:` line in `attr/_make.py`), and `docs/conf.py` sets neither `default_role` nor an intersphinx mapping. A `sphinx-build -W` run may warn on these. No doc build is part of this run.
5. `docs/api.rst` ends without a trailing newline on its last line (`.. autofunction:: attr.has`).

Line lengths in all five touched files are within the project's flake8 limit (longest new line is under 80 characters), so style is not an issue.

## Verdict

VERDICT: changes_needed

## Experience difference

Ticket-described product vs. what exists now:

- **`attr.has(cls)`** — exists. Returns `True` when every attribute of `cls` is an `attr.Attribute` instance, `False` otherwise. The documented `TypeError` for a non-class argument is real, but it carries a different message from `ls`'s `ValueError` for the same mistake, and nothing tests either.

- **`attr.ls(cls)`** — exists. Returns `cls.__attrs_attrs__` in definition order, as a list of `attr.Attribute` objects. No-argument call falls back to the calling frame's locals. The one clear mismatch is the docstring example: it shows a compact single-line repr, but `attr/_dunders.py` performs no wrapping, so what a user actually sees in a REPL is a multi-line repr. Reading the docs gives the wrong visual expectation of the output.

- **`attr.to_dict(inst)`** — exists, with `recurse=True` by default and `recurse=False` for a flat dict. Works as the ticket describes. Nothing about it is tested, so this is verified only by the docs.

- **`attr.Attribute` as a public name** — importable from `attr` (`attr/__init__.py` adds it to imports and `__all__`). The class is generated via `attr.s`, so it gets a generated repr and ordering. Its `from_counting_attr` constructor is documented only in the internal `attr/_make.py` docstring, not on the public API page in `docs/api.rst`, so a user reading the documentation site sees the type but not how to build one that supports counted fields.

- **Documentation** — `docs/api.rst` gained sections for `ls`, `has`, `to_dict` and the `Attribute` class. The page is not build-verified in this run, and three things are unresolved: the single-backtick roles with no `default_role`/`intersphinx` configured in `docs/conf.py`, the missing trailing newline, and the fact that the examples are doctest-shaped but have no `doctest_global_setup` import of `attr`, so `sphinx.ext.doctest` is enabled for examples that cannot currently execute.

- **Test coverage** — this is the widest gap. The ticket called out `tests/test_funcs.py`, and it is unchanged. The suite reports green at 8/8, but those 8 tests were already there. Nothing in the suite exercises the new `has`, the public `Attribute` re-export, or the ordering and contents of `ls`.

- **Documentation-to-behaviour agreement for docstrings** — the ticket's point is that these helpers ship documented examples a user can copy. Today the examples are unexecuted, and at least one (`ls`) does not match what the code prints.