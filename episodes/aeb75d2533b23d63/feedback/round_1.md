# Feedback report

## Tests

The harness ran the project suite three times for this workspace:

- Run 1: `python -m pytest` — exit_code=0, output ends with
  `62105 passed, 417 deselected in 103.15s (0:01:43)`
  (`collected 62522 items / 417 deselected / 62105 selected`).
- Run 2: `python -m pytest` — exit_code=0, output ends with
  `62105 passed, 417 deselected in 103.57s (0:01:43)`.
- Run 3: `python -m pytest` — exit_code=0, output ends with
  `62105 passed, 417 deselected in 104.66s (0:01:44)`.

Total selected: 62105. Passed: 62105. Failed: 0 (all three runs). The
`tests/test_dependency_groups.py` file, which holds the cycle roundtrip check,
is listed as fully passing (`.......................................`). I did not run
any test command myself; these numbers are quoted from the harness output.

## What is missing

Nothing that the ticket asked for is missing, based on what I inspected:

- `src/packaging/dependency_groups.py` — `CyclicDependencyGroup` gets a
  `__reduce__` that returns the class plus the three group-name arguments, so
  the exception survives a pickle roundtrip.
- `src/packaging/metadata.py` — `InvalidMetadata` gets a `__reduce__` that
  returns the class plus `(field, message)`, so it survives a pickle roundtrip.
- The two roundtrip checks the ticket names exist and passed in the harness run:
  `tests/test_dependency_groups.py` (cyclic include pickle roundtrip, comparing
  class, all three group names and `str(copy) == str(exc)`) and
  `tests/test_metadata.py` (`TestInvalidMetadata.test_pickle_roundtrip`,
  comparing class, `field` and message).

I checked both `__reduce__` argument tuples against the constructors and the
order matches, so the reconstructed object is identical to the original.

## Why it fails

It does not fail. All three harness runs exited 0 with 62105 passed and 0
failed, so there is no failing test to explain.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes exceptions from this library that can be pickled and
unpickled without losing information. What exists now matches that description
for the two exception types involved:

- Before the change, unpickling a `CyclicDependencyGroup` or an
  `InvalidMetadata` would rebuild the object from `args` only. With the
  `__reduce__` methods in place, a roundtrip keeps the same class, the same
  message text, and the extra attributes — the requested/group/include group
  names for the cycle error, and the `field` for the metadata error.
- A user who catches one of these errors in one process and sends it (or a
  traceback/deepcopy) to another process now gets the same type and the same
  message and attributes back, instead of a differently-populated object.
- The rest of the library behaviour is unchanged: the full suite still passes
  62105 tests with 0 failures in each of the three runs, so nothing else
  regressed.

The one neutral observation I will record without treating it as a defect: the
two roundtrip tests are present in the tree alongside the source change; whether
they were added by this change or already existed does not affect the user-facing
behaviour, and both pass in the harness output.