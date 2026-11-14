# Feedback report

## Tests

The harness ran the Diff2 suite three times; I did not run any test myself.

Command: `python -m pytest`

- Run 1 (exit_code=0): `62102 passed, 417 deselected in 155.11s`
- Run 2 (exit_code=0): `62102 passed, 417 deselected in 122.48s`
- Run 3 (exit_code=0): `62102 passed, 417 deselected in 146.93s`

Totals across each run: 62102 selected tests passed, 0 failed, 417 deselected (62519 collected). The harness output also shows the file-level line for this change:

```
tests/test_dependency_groups.py ......................................   [  0%]
```

So all 38 tests in `tests/test_dependency_groups.py` passed in every run, including the malformed-requirement test this ticket is about.

## What is missing

Nothing the ticket asked for is missing. The ticket describes one behavioral change (an unparseable requirement string in a dependency group should be reported as a collected `InvalidRequirement` together with the group-level "malformed" error instead of escaping on its own) and this is present.

I read `/workspace/src/packaging/dependency_groups.py` and saw the change:

- line 7: `from .requirements import InvalidRequirement, Requirement` (the import was widened to bring in `InvalidRequirement`)
- lines 247-248: the string branch now wraps the parse in the collector instead of calling `Requirement(item)` bare:

  ```
  with errors.collect(InvalidRequirement):
      elements.append(Requirement(item))
  ```

I read `/workspace/src/packaging/errors.py` and confirmed `_ErrorCollector.collect` (lines 74-87) catches the listed error classes and appends them to `self.errors`, and that `dependency_groups._parse_group` returns `()` when `errors.errors` is non-empty, so the collected error is folded into the group-level failure that `lookup`/`resolve` finalize with `"[dependency-groups] data for {group!r} was malformed"`. That matches the ticket's "What changed" and "User experience" text.

The ticket's described behavior is covered by the test I read at `/workspace/tests/test_dependency_groups.py` lines 466-487, `test_resolution_collects_invalid_requirement_with_sibling_errors`, which asserts both `_group_contains(excinfo, InvalidRequirement)` (line 485) and `_group_contains(excinfo, InvalidDependencyGroupObject)` (line 487) inside an `ExceptionGroup` matching `"[dependency-groups] data for 'all' was malformed"` (line 480). This test passes in all three runs above.

## Why it fails

No test failed. All three harness runs exited 0 with `62102 passed`, 0 failures. There is nothing to explain.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a user who writes a dependency group whose value list contains a string that is not a valid PEP 508 requirement (for example a typo, or something that is not a requirement at all). The intended product experience is that this bad item does not crash the whole call with a lone, unexplained parse error while silently ignoring any other, separate problem in the same call. Instead the bad requirement is recorded while the rest of the group is processed, and the final error the user sees is the group-level statement `[dependency-groups] data for '<group>' was malformed`, with the malformed requirement carried as one of the collected sub-errors. If there are other independent problems at the same time, the user sees them all together rather than only whichever one happened to raise first.

The product that exists now matches that description. In the code I read, `_parse_group` runs the `Requirement(item)` parse inside `errors.collect(InvalidRequirement)` (`dependency_groups.py:247-248`), the collector stores it rather than letting it escape (`errors.py:74-87`), and the group-level malformed error is what is ultimately raised, with the `InvalidRequirement` included in the aggregated group. The one caveat I can state honestly is that I verified this from reading the source plus the harness showing the dedicated test `test_resolution_collects_invalid_requirement_with_sibling_errors` passing; I did not execute anything myself, and the harness output I was given is the only runtime evidence, which shows 0 failures across three full runs.

One thing worth noting as simply an observation, not a defect: the ticket did not ask for changelog, docs, or doctest updates, so I am not treating the absence of any of those as missing work. No user-facing behavior in the ticket is left unimplemented.