# Feedback report

## Tests
The pipeline ran the project suite three times: `python -m pytest` (rootdir `/workspace`, configfile `pyproject.toml`). All three runs are identical and exit 0:

- collected 166 items
- `165 passed, 1 skipped in 2.66s` (run 1)
- `165 passed, 1 skipped in 2.65s` (run 2)
- `165 passed, 1 skipped in 2.58s` (run 3)

Failures: 0. The skipped item is in `tests/test_asyncio.py` (shown as `...s...`), unrelated to this change. All tests, including the ones in `tests/test_tenacity.py`, pass.

## What is missing
Nothing that the ticket asked for. The ticket asks for two things: (1) building an empty `wait_chain` should fail right away with a clear message, and (2) the same clear error should show up when such a chain is used by a retry. I read `tenacity/wait.py`, which now has, at the top of `wait_chain.__init__`:

- `tenacity/wait.py:107`: `if not strategies:`
- `tenacity/wait.py:108`: `raise ValueError("A wait_chain needs at least one wait strategy")`

Construction now raises immediately, so an empty chain can never be built and handed to `Retrying`; the network of the second requirement is covered as a result. I also read `tests/test_tenacity.py:544` `test_wait_chain_requires_at_least_one_strategy`, which checks `ValueError` from `tenacity.wait_chain()` and from `Retrying(wait=tenacity.wait_chain())`. Both requirements have a matching test, and the suite passes.

## Why it fails
No failing tests. All three harness runs report `165 passed, 1 skipped` with exit code 0, so there is nothing to explain here.

## Verdict
VERDICT: approve

## Experience difference
Before this change, calling `tenacity.wait_chain()` with no strategies built a chain object with an empty strategy list and returned it without complaint. The problem only appeared later, deep inside a retry: when the wait logic ran and tried to index the empty list (`self.strategies[wait_func_no - 1]` in `tenacity/wait.py:113`), the user got an opaque `IndexError` from inside the library, far from the line of their own code that caused it, and with no hint about what was wrong.

After this change, the same mistake is caught at the moment the user writes it. `tenacity.wait_chain()` raises a `ValueError` with the plain message "A wait_chain needs at least one wait strategy" as soon as the chain is created, so the user sees the error at the call site and the message names the actual problem. The same clear `ValueError` surfaces when that construction is used inline as `Retrying(wait=tenacity.wait_chain())`. Chains built with one or more strategies behave exactly as before; no existing behavior is changed. The user-visible difference is therefore: louder, earlier, clearer error instead of a silent accept followed by a confusing `IndexError` during retries.
