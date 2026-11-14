# Feedback report

## Tests

The pipeline ran the suite three times. All three runs passed.

Command (harness): `python -m pytest`

- Run 1 of 3: exit code 0 — `collected 4 items` / `tests/test_context.py .... [100%]` / `4 passed in 0.03s`
- Run 2 of 3: exit code 0 — `collected 4 items` / `tests/test_context.py .... [100%]` / `4 passed in 0.04s`
- Run 3 of 3: exit code 0 — `collected 4 items` / `tests/test_context.py .... [100%]` / `4 passed in 0.04s`

Total: 4 tests collected, 4 passed, 0 failed, 0 errors, in each of the three runs.

I did not run the tests myself in this round; the numbers above are quoted from the harness output only.

## What is missing

Nothing the ticket asked for is absent.

- `Context.ensure_object` is implemented: `click/core.py:136-143` — `def ensure_object(self, object_type):` ... `rv = self.find_object(object_type)` / `if rv is None:` / `self.obj = rv = object_type()` / `return rv`.
- `make_pass_decorator` takes `ensure`: `click/decorators.py:28` — `def make_pass_decorator(object_type, ensure=False):`, with the parameter documented at `click/decorators.py:52-55`.
- The new behaviour is implemented in the decorator: `click/decorators.py:61-67` — `obj = ctx.find_object(object_type)` / `if obj is None:` / `if not ensure:` / `raise RuntimeError(...)` / `ctx.obj = obj = object_type()`.
- The docs hint is covered: `docs/complex.rst` has an "Ensuring Objects" section and the `Repo` example there now takes defaults (`docs/complex.rst:85`, `def __init__(self, home="."):`).
- Tests for both new behaviours are present in `tests/test_context.py`.

One small note, not a blocker and not a ticket item: the docstring at `click/decorators.py:46-48` says "If `ensure` is `True` then :meth:`Context.ensure_object` is used instead of :meth:`Context.find_object`", but the body at `click/decorators.py:61-67` calls `ctx.find_object(object_type)` and writes `ctx.obj = obj = object_type()` itself. So the new `Context.ensure_object` is dead code inside the library — nothing calls it. The user-visible result is the same, so this is a wording/duplication issue, not a behaviour issue.

## Why it fails

No test failed, so there is nothing to explain here.

## Verdict

VERDICT: approve

## Experience difference

The product the ticket describes and the product that exists now behave the same from a user's point of view.

- Old behaviour kept: running a subcommand without a parent object still fails the same way. `click/decorators.py:63-66` raises `RuntimeError('Managed to invoke callback without a context object of type %r existing' % object_type.__name__)`, which is the same text as before the change, and `tests/test_context.py:73-93` (`test_get_context_objects_missing`) checks that exact message. Existing programs that rely on this error see no difference.
- New behaviour, case 1: a subcommand invoked on its own now runs instead of erroring. `tests/test_context.py:33-51` (`test_ensure_context_objects`) builds a `Repo` command with `@pass_repo.ensure`, invokes it with `obj=None`, and checks `runner.invoke(repo, ["init"])` plus `runner.invoke(repo, ["status"])` both succeed.
- New behaviour, case 2: an object created by an outer command is still shared. `tests/test_context.py:94-118` (`test_get_context_objects`) builds `repo` with `Repo("repo")`, invokes `["status"]`, and checks `ctx.obj.home == "repo"`.
- Both `ensure` and non-`ensure` paths are covered, so the flag is tested on and off.
- Docs: `docs/complex.rst` now shows `Repo.__init__` with a default value and adds an "Ensuring Objects" section using `@pass_repo.ensure`, so the documented path is the new one.
- Not verified by the test run: `docs/complex.rst` is checked only when the documentation is built (the `click:example` / `click:run` directives in `docs/clickdoctools.py`), which `python -m pytest` does not exercise. The four passing tests do not prove the doc example runs.
- Small user-visible wrinkle worth knowing: because the decorator creates the object itself (`click/decorators.py:67`) rather than calling `Context.ensure_object`, anyone subclassing `Context` and overriding `ensure_object` will not see their override used by `ensure=True`. `click/core.py:136-143` behaves correctly when called directly.