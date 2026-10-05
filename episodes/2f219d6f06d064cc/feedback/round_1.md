# Feedback report

## Tests

The pipeline ran `python -m pytest` three times in `/workspace` (I did not run tests myself).
All three runs exited 0 with the same result.

- Total collected: **1359**
- Passed: **1351**
- Failed: **0**
- Skipped: **7**
- Xfailed: **1**

Run 1 of 3: `python -m pytest`, exit_code=0.

```
collected 1359 items
...
SKIPPED [1] tests/test_functional.py:775: requires Python 3.13+
SKIPPED [1] tests/test_functional.py:784: requires Python 3.13+
SKIPPED [1] tests/test_functional.py:798: requires Python 3.13+
SKIPPED [1] tests/test_make.py:2662: Pre-3.10 only.
SKIPPED [1] tests/test_pyright.py:35: Requires pyright.
SKIPPED [1] tests/test_pyright.py:83: Requires pyright.
SKIPPED [1] tests/test_slots.py:503: slots without weakref_slot should only work on PyPy
XFAIL tests/test_setattr.py::TestSetAttr::test_slotted_confused
========= 1351 passed, 7 skipped, 1 xfailed in 15.08s ==================
```

Runs 2 and 3 are identical: `1351 passed, 7 skipped, 1 xfailed` (15.14s and 15.59s),
exit_code=0 both times.

Note on what the skip list means for this change: the two pyright tests
(`tests/test_pyright.py:35`, `:83`, both "Requires pyright") were skipped, so the
stub change in `src/attr/validators.pyi` was checked by the pytest run only through
whatever mypy coverage exists in this environment, not through pyright.

## What is missing

The change is `git diff --cached --stat`:

```
 changelog.d/1449.change.md |  1 +
 src/attr/validators.py     | 44 +++++++++++++++++++++++++++++++++++---------
 src/attr/validators.pyi    | 14 +++++++-------
 3 files changed, 43 insertions(+), 16 deletions(-)
```

1. **No runtime test for the new list/tuple arguments.** `tests/test_validators.py` is
   not in the diff. A grep over `tests/` for
   `member_validator=[|iterable_validator=[|key_validator=[|value_validator=[|mapping_validator=[|and_([`
   returns only three hits, all in the static-typing file:

   ```
   tests/typing_example.py:239:            key_validator=[attr.validators.instance_of(C)],
   tests/typing_example.py:240:            value_validator=[attr.validators.instance_of(C)],
   tests/typing_example.py:241:            mapping_validator=[attr.validators.instance_of(dict)],
   ```

   The list cases for `deep_iterable` are at `tests/typing_example.py:201-204`. That file is
   type-checked, not executed for behaviour, so nothing asserts that a list of validators
   actually raises when one member fails. The ticket named `tests/test_validators.py` under
   Hints, so this is not a hard requirement, but it is the one real gap.

2. **Version numbers in the two docstrings disagree.** Both `versionchanged` lines added to
   `deep_iterable` say `24.1.0`, in `src/attr/validators.py`:

   ```
   .. versionchanged:: 24.1.0 *member_validator* can be a list of validators.
   .. versionchanged:: 24.1.0 *iterable_validator* can be a list of validators.
   ```

   while the ones added to `deep_mapping` in the same commit say `25.4.0`:

   ```
   .. versionchanged:: 25.4.0
      *key_validator*, *value_validator*, and *mapping_validator* can now be
      lists or tuples of validators.
   ```

   The ticket asks to note the behaviour "as of version 25.4.0". I am not certain which is
   intended for `deep_iterable`, so I am not calling it a defect, only an inconsistency
   inside one commit.

3. **`deep_iterable` docstring omits tuples.** It says "can be a list of validators"; the
   `deep_mapping` note for the same commit says "lists or tuples". The code accepts both
   (`isinstance(validators, (list, tuple))` in `_join_validators`, `src/attr/validators.py:23`).

## Why it fails

Nothing fails. There are 0 failed tests across all three runs, so this section is empty.
The items above are gaps in coverage and documentation wording, not test failures, and none
of them is a behaviour bug.

## Verdict

VERDICT: approve

## Experience difference

What a user gets from the change, versus what the ticket describes:

- `deep_iterable(member_validator, iterable_validator)` now accepts a list or a tuple for
  **both** arguments. The diff replaces the old inline handling, which only covered
  `member_validator`, with a shared helper applied to both:

  ```python
  return _DeepIterable(
      _join_validators(member_validator),
      _join_validators(iterable_validator),
  )
  ```

  So `deep_iterable([instance_of(C), instance_of(D)])` works, and so does
  `deep_iterable(member, [instance_of(list), instance_of(tuple)])`. Before, a list in the
  second position would have been called as a plain callable and blown up at validation time.

- `deep_mapping` now accepts lists or tuples for `key_validator`, `value_validator` and
  `mapping_validator`:

  ```python
  return _DeepMapping(
      _join_validators(key_validator),
      _join_validators(value_validator),
      _join_validators(mapping_validator),
  )
  ```

  Passing a single validator, as before, takes the same path as before: `_join_validators`
  returns the argument untouched when it is not a list or tuple, so single-validator behaviour
  and the "at least one of key_validator or value_validator" `ValueError` are unchanged.

- Combines them with `and_()`, so every validator in the list must pass, and failures still
  surface as `TypeError` with the attribute name and value, exactly as a single validator did.

- Both the stub file and the runtime agree. All four parameters in `src/attr/validators.pyi`
  use `_ValidatorArgType`, which already covers the single-validator and
  `list | tuple` shapes, so a type checker accepts the new calls and mypy/pyright users see
  no error for list arguments.

- The changelog fragment `changelog.d/1449.change.md` describes the new capability in
  user-facing wording, so the change is announced.

Where the experience is short of the ticket:

- A user cannot tell from the shipped documentation alone that a list of validators must have
  *every* member pass, and the two docstrings name different versions and different
  list/tuple wording for the same behaviour.
- An empty list or tuple reaches `and_()` with no arguments. The ticket does not say what
  should happen there, so I did not treat it as a defect, but it is an undefined corner.
- Runtime behaviour of the new arguments is covered only by type-check examples, so a
  regression that dropped `and_()` from the list path would not be caught by the pytest run.