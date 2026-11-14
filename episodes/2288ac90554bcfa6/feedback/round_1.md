# Feedback report

## Tests

The pipeline ran the project suite three times. All three runs passed.

Command: `python -m pytest` (rootdir `/workspace`, configfile `pyproject.toml`, `testpaths = tests`).

```
collected 62850 items / 427 deselected / 62423 selected
...
=============== 62423 passed, 427 deselected in 78.90s (0:01:18) ===============
```

Run 1: exit code 0 — 62423 passed, 0 failed, 427 deselected (78.90s).
Run 2: exit code 0 — 62423 passed, 0 failed, 427 deselected (77.79s).
Run 3: exit code 0 — 62423 passed, 0 failed, 427 deselected (79.90s).

No test failed in any run, so there is no failing node id to report.

The tests that cover this ticket are in `tests/test_metadata.py`:
- `tests/test_metadata.py:720` — `"summary", ["Hello\n    Again", "Hello\rAgain", "Hello\u2028Again"]`, i.e. the pre-existing plain-newline case plus a bare `\r` and a `\u2028`.
- `tests/test_metadata.py:1500` — `test_headers_fold_every_line_boundary`, parameterised at `tests/test_metadata.py:1497-1498` over `["\r", "\r\n", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"]`, asserting both the exact written text and the value read back by `email.message_from_string`.

I did not run the suite myself this round. I ran one small smoke check outside the suite (`PYTHONPATH=/workspace/src python -c ...`), which printed a folded header `'Author: A\n        some\nSummary: x\n         y\n\n'` and `'summary' must be a single line` for `Hello\rAgain` and for `Hello\vAgain\u2029Z\x1fQ`.

## What is missing

Nothing that the ticket asks for. Each point in "What should happen" (line 9 of the ticket) and "What changed" (line 21) maps to code I read:

- Writing metadata folds every line separator instead of raising. `src/packaging/metadata.py:196-213` builds `_LINE_BREAKS_RE` from `"\r\n", "\r", "\n", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x1f", "\x85", "\u2028", "\u2029"`, and `src/packaging/metadata.py:218` defines `_fold_line_breaks`.
- Setting a field directly behaves the same way. The fold is applied in `RFC822Policy.header_store_parse` at `src/packaging/metadata.py:354`, which is the policy path used by `RFC822Message.__setitem__`, so direct assignment and parsed writing share one code path.
- The space is still added after the fold. `src/packaging/metadata.py:355` keeps the original `value.replace("\n", "\n" + " " * size)`.
- The summary check rejects all of those breaks with the existing message. `src/packaging/metadata.py:676-677` is `if _LINE_BREAKS_RE.search(value): raise self._invalid_metadata(f"{self.raw_name!r} must be a single line")`.
- The docstring for the summary field was updated at the same place (`src/packaging/metadata.py:967` region) to say it must not contain any line break, not just `\n`.

`CHANGELOG.rst:89-93` describes the change. I am not treating anything about that entry as missing work.

## Why it fails

No test fails, so this section is empty. Nothing to explain.

## Verdict

VERDICT: approve

## Experience difference

Before the change, two things went wrong, and both are now different in the shipped code.

**Writing a field that holds a line break.** Before, if any value written into a metadata message contained a carriage return, a form feed, a line separator (`\u2028`), a paragraph separator (`\u2029`), a group/file/record/unit separator (`\x1c`–`\x1f`) or the next-line character (`\x85`), the write stopped with an error about a folded header containing a newline, and no metadata text came back at all. Only a plain `\n` was understood as a line break. Now, `src/packaging/metadata.py:354` converts every one of those separators to `\n` before the existing fold, and `src/packaging/metadata.py:355` indents the continuation by `len(name) + 2` spaces. So `message["Author"] = "A\rsome"` produces `Author: A\n        some`, which `email` reads back as the single value `"A\n       some"` — one continuous field, not two fields. Windows input built as CRLF, or a stray CR left on its own, now writes instead of raising. Setting a field on an `RFC822Message` directly and writing a parsed message both go through `header_store_parse`, so they behave identically, which is the "setting a field on a metadata message directly behaves the same way" part of the ticket.

**A summary with a bare carriage return.** Before, the check looked only for `\n`, so `Summary: Hello\rAgain` was accepted and handed back unchanged as if it were one line, and readers downstream saw two lines where the author declared one. Now `src/packaging/metadata.py:676` searches the same separator set, so that input raises `InvalidMetadata` with the existing text `'summary' must be a single line` — the same message the plain-newline case has always produced, so callers that match on it need no change. Every separator is covered, not just CR and `\u2028`; `tests/test_metadata.py:720` pins CR and LS, and `Hello\vAgain\u2029Z\x1fQ` is also rejected in the smoke check I ran.

**What did not change.** Values that already contained only a plain newline are written byte-for-byte as before, because `_fold_line_breaks` maps `\n` to `\n` and the original `replace` on line 355 is untouched. The pre-existing plain-newline rejection of a summary is kept at `tests/test_metadata.py:720` (`"Hello\n    Again"`). No public name was added or removed; `_LINE_BREAKS_RE` and `_fold_line_breaks` are module-private.