# Feedback report

## Tests

The pipeline ran the Diff2 suite three times, all with the same command `python -m pytest` in `/workspace`, and all exited 0. Each run collected 128 items and reported **127 passed, 1 skipped, 0 failed**. Real output excerpt (run 1):

```
collected 128 items

tests/test_after.py ...                                                  [  2%]
tests/test_asyncio.py ........s.............                             [ 19%]
tests/test_issue_478.py ..                                               [ 21%]
tests/test_tenacity.py ................................................. [ 59%]
..............................................                           [ 95%]
tests/test_tornado.py ....                                               [ 98%]
tests/test_utils.py ..                                                   [100%]

======================== 127 passed, 1 skipped in 2.46s ========================
```

Runs 2 and 3 produced the same result: `127 passed, 1 skipped` (in 2.47s and 2.45s). No test failed in any run. `tests/test_after.py` shows 3 passing tests (`...`), which matches the three tests in that file: `test_01_default`, `test_02_none_seconds_since_start`, and `test_02_custom_sec_format`.

## What is missing

Nothing that the ticket asked for is missing. The ticket asks that when `seconds_since_start` is missing the `after_log` line is still written with `?` in place of the seconds number, and that is implemented in `tenacity/after.py` (staged diff): lines 42-45 add

```
if retry_state.seconds_since_start is None:
    seconds_since_start = "?"
else:
    seconds_since_start = sec_format % retry_state.seconds_since_start
```

and line 49 interpolates that value into the log message. The three `tests/test_after.py` tests cover the default wording, the `?` case, and a custom `sec_format`, and all pass.

## Why it fails

No test fails. All three pipeline runs exited 0 with `127 passed, 1 skipped`.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes an `after_log` that never crashes and never omits the log line when the elapsed-time value is unavailable. In the product that exists now, a user who calls a retry-decorated function still gets the usual line when timing is available — `tenacity/after.py` keeps the original `"Finished call to '%s' after %s, this was the %s time calling it."` wording for the normal path (as asserted by `test_01_default`), and still honors a custom `sec_format` (as asserted by `test_02_custom_sec_format`). In the case where `seconds_since_start` is `None` (e.g. when `outcome_timestamp` was not set), the user now sees the same sentence with `?` where the seconds would be — `"Finished call to '<fn>' after ?(s), this was the <n>th time calling it."` — instead of an error or a broken format. The call name and the try count stay intact, so the log remains readable and useful. There is no other change to the user-visible behaviour; the full suite passes with `127 passed, 1 skipped` in each of the three runs, so nothing else regressed.
