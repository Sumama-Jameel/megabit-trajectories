# Feedback report

## Tests

The harness ran the project suite three times (`python -m pytest`, rootdir `/workspace`, configfile `pyproject.toml`, testpaths `tests`). All three runs exited 0 and collected **1362 items**:

- Run 1: `================= 1354 passed, 7 skipped, 1 xfailed in 23.92s ==================` (exit_code=0)
- Run 2: `================= 1354 passed, 7 skipped, 1 xfailed in 22.40s ==================` (exit_code=0)
- Run 3: `================= 1354 passed, 7 skipped, 1 xfailed in 21.78s ==================` (exit_code=0)

So: 1354 passed, 0 failed, 7 skipped, 1 xfailed, 1362 collected. The skips are environment-gated, not failures:
`tests/test_functional.py:775`, `:784`, `:798` (requires Python 3.13+), `tests/test_make.py:2834` (Pre-3.10 only), `tests/test_pyright.py:35` and `:83` (Requires pyright), `tests/test_slots.py:503` (slots without weakref_slot should only work on PyPy). The xfail is `tests/test_setattr.py::TestSetAttr::test_slotted_confused`. No failing test exists, so there is nothing for "Why it fails".

## What is missing

I found no ticket-required behaviour that is absent. The changed files and the behaviour points I confirmed by reading them:

- `src/attr/_make.py:117` — `kw_only=None,` in `attrib(...)`, i.e. the "unset" sentinel now exists for `attr.ib`/`attrs.field`.
- `src/attr/_make.py:380-381` — `_transform_attrs` signature gained `force_kw_only,`.
- `src/attr/_make.py:451-463` — `if kw_only:` branch: with `force_kw_only=True` (`:452-454`) both `own_attrs` and `base_attrs` are evolved to `kw_only=True`; otherwise (`:457`) only own attrs are evolved, and only when `a.kw_only is None` (`a.evolve(kw_only=True) if a.kw_only is None else a`); `:463` resolves the remaining `None` sentinels to `False` (`a.evolve(kw_only=False) if a.kw_only is None else a`). This is the field-level `kw_only=False` "opt out" plus the diagonal/class-level-only behaviour.
- `src/attr/_make.py:1363-1364` — `attr.s` keeps the old wide behaviour as the default: `kw_only=False,` / `force_kw_only=True,`.
- `src/attr/_next_gen.py:36-37` — `attrs.define(kw_only=False, force_kw_only=False)`; passed through at `_next_gen.py:365-366`; documented at `_next_gen.py:221-225` ("Force the *kw_only* setting to apply to all fields, including those inherited from base classes. By default (``False``), ...").
- `src/attr/_next_gen.py:435` — `attrs.field(..., kw_only=None)`, forwarded at `_next_gen.py:601`, documented at `_next_gen.py:561-565` ("If left ``None``, the value of the class-level ``kw_only`` is used").
- Stubs cover the widened parameter: `src/attr/__init__.pyi:179,203,226,249` and `src/attrs/__init__.pyi:80,104,127,150` are `kw_only: bool | None = ...`; `force_kw_only: bool = ...` at `src/attr/__init__.pyi:271,300,343` and `src/attrs/__init__.pyi:173,200,230,257`.
- Repo tests exercising this: `tests/test_make.py:1041` (`force_kw_only=True` propagates to subclass attrs), `tests/test_make.py:1063,1139` (`@attr.s(kw_only=True, force_kw_only=False)`), `tests/test_make.py:1144,1221,1227,1233` (`@attr.define(..., force_kw_only=True)`), `tests/test_make.py:1216` (`test_kw_only_inheritance_force_kw_only`), `tests/test_make.py:2060` (`force_kw_only=False` in a `_ClassBuilder` construction).

Two non-blocking observations (housekeeping, not required work per the review rules, so not defects and not blocking): the `attr.s` docstring at `src/attr/_make.py:1416` still only says `.. versionadded:: 18.2.0 *kw_only*` and does not mention `force_kw_only`, whereas the `attrs.define` docstring was updated at `_next_gen.py:221`; and no `changelog.d/*.change.md` fragment was added for this feature (`ls changelog.d/` lists only `1427.change.md`, `1446.change.md`, `1448.change.md`, `1449.change.md`, `1451.change.md`, `towncrier_template.md.jinja`). `git status --porcelain` shows the staged change set is `M src/attr/__init__.pyi`, `M src/attr/_make.py`, `M src/attr/_next_gen.py`, `M src/attrs/__init__.pyi`, plus `A pytest_full.log`.

## Why it fails

Nothing fails. The harness reported `0 failed` in all three runs (`1354 passed, 7 skipped, 1 xfailed`, exit_code=0 each time); the only non-passing items are the environment-gated skips listed above and one pre-existing xfail, `tests/test_setattr.py::TestSetAttr::test_slotted_confused`.

## Verdict

VERDICT: approve

## Experience difference

The ticket asks for a keyword-only story where the class-level `kw_only` setting only affects the class's own fields, where an individual field can override that setting in either direction, and where the previous sweeping behaviour stays reachable. What exists now matches that description.

Concretely, as a user you get: `attrs.define(kw_only=True)` makes only the fields declared on that class keyword-only and leaves fields inherited from a base class in the form they were defined in — but does not disturb a base field that already made its own choice — while `attrs.define(kw_only=False)` (the default) leaves everything as-is. A field can opt out of the class setting with `attrs.field(kw_only=False)` / `attr.ib(kw_only=False)`, and the new `kw_only=None` default means "do not override, just follow the class-level setting"; previously, passing a value was the only way to express anything, so a field could not say "explicitly positional" when the class said `kw_only=True` (`src/attr/_make.py:451-463`). The old, more aggressive behaviour — where `kw_only=True` on a subclass also rewrote inherited fields — is still available by passing `force_kw_only=True`, and the choice of default differs by entry point: `attr.s` / `attr.make_class` default to `force_kw_only=True` so existing code keeps its current behaviour (`src/attr/_make.py:1363-1364`), while `attrs.define` / `attrs.frozen` default to `force_kw_only=False` so new code gets the narrower behaviour (`src/attr/_next_gen.py:36-37`, `_next_gen.py:365-366`). Generated `__init__` signatures follow from this: fields with `kw_only is False` stay positional and the rest move after the `*` (`src/attr/_make.py:474-478`).

Type-checker users see the same story: `attrs.field`/`attrib` accept `bool | None` for `kw_only`, and `attrs`/`make_class`/`define`/`frozen` all expose `force_kw_only: bool` in the stubs (`src/attr/__init__.pyi:179,203,226,249,271,300,343`; `src/attrs/__init__.pyi:80,104,127,150,173,200,230,257`). Documentation-wise, `attrs.define` and `attrs.field` explain both the new `force_kw_only` flag and the `None` sentinel (`src/attr/_next_gen.py:221-225`, `:561-565`), while the `attr.s`/`attr.ib` docstrings were not extended to mention `force_kw_only` — the only user-visible gap I noticed, and it does not change any behaviour or any test result.