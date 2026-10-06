# Feedback report

## Tests

The harness ran the Diff2 suite three times: `python -m pytest` (rootdir `/workspace`, configfile `pyproject.toml`, testpaths `tests`, Python 3.11.16). All three runs passed with exit code 0.

- Run 1: `============================= 1373 passed, 8 skipped, 1 xfailed in 16.80s ==============================`
- Run 2: `1373 passed, 8 skipped, 1 xfailed in 15.07s`
- Run 3: `1373 passed, 8 skipped, 1 xfailed in 17.04s`

Collected items in each run: `collected 1382 items`. So: 1382 collected, 1373 passed, 8 skipped, 1 xfailed, 0 failed — in every one of the three runs.

The skips and xfail are unrelated to this change (e.g. `SKIPPED [1] tests/test_functional.py:795: requires Python 3.13+`, `SKIPPED [1] tests/test_pyright.py:35: Requires pyright.`, `XFAIL tests/test_setattr.py::TestSetAttr::test_slotted_confused`).

## What is missing

Nothing. The ticket asked for the frozen-object error to carry its own message. The change in `src/attr/exceptions.py` gives `FrozenError` its own `__init__(self, *args)` that defaults to `(self.msg,)` when no args are passed, so each instance carries its own message and the shared mutable class-level list (`args: ClassVar[tuple[str]] = [msg]`) is gone. `msg = "can't set attribute"` on `src/attr/exceptions.py:17` stays `"can't set attribute"`, so the message equals the first argument. `src/attr/exceptions.pyi` gained `def __init__(self, *args: Any) -> None: ...` so the stub matches the new runtime signature. The raise sites (`src/attr/setters.py:35`, `src/attr/_make.py:573,584,2554`) raise `FrozenInstanceError`/`FrozenAttributeError` with no args and therefore pick up the default message. `tests/test_functional.py:268–280` (inside `TestFrozen::test_frozen_instance`, both slotted and non-slotted) already checks set and delete produce `e.value.msg == e.value.args[0] == "can't set attribute"`, and that test passed. `src/attrs/exceptions.py` re-exports from this module, so `attrs.exceptions.FrozenError` is covered without a separate edit. No ticket requirement is unaddressed.

## Why it fails

No test failed. All three runs report `0 failed` (`1373 passed, 8 skipped, 1 xfailed`) with exit code 0. There is nothing to explain.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a product where the error raised on a frozen object's set/delete carries its own message instead of sharing one changeable class-level value, and where the message is the exception's first argument. The product that exists now matches this: `FrozenError.__init__` gives every instance its own args, defaulting to the message `"can't set attribute"` when raised with none, and `msg` remains an immutable string equal to `args[0]`. Setting or deleting an attribute on a frozen `attrs` class still raises `FrozenInstanceError` (or `FrozenAttributeError` for a non-frozen attribute on a frozen class) with the same `"can't set attribute"` text as before, so the user-visible message and `pytest.raises(match=...)` behavior are unchanged. The public class hierarchy (`FrozenInstanceError` and `FrozenAttributeError` subclassing `FrozenError`) and the `attrs.exceptions` re-export are intact. The removed `ClassVar` also matches the ticket's intent that the error no longer shares one mutable list across all instances. The `.pyi` stub was updated in step with the runtime, keeping type-checked users in sync. One small nuance in wording: the ticket's phrase "its own fixed copy of the text" is satisfied in the sense that each instance gets its own `args` tuple, though the text string itself is still the single class-level `msg` constant on line 17 (unchanged, and that is what the ticket also asks — `msg == "can't set attribute"`). I found no other user-visible difference from the ticket's described product.