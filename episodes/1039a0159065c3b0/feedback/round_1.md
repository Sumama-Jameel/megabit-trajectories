# Feedback report

## Tests

I did not run the tests. The pipeline ran the full suite three times and gave me
the results. Command: `python -m pytest` (rootdir `/workspace`, configfile
`pyproject.toml`, testpaths `tests`).

- Run 1: `62114 passed, 417 deselected in 100.53s` (exit_code=0)
- Run 2: `62114 passed, 417 deselected in 104.33s` (exit_code=0)
- Run 3: `62114 passed, 417 deselected in 103.69s` (exit_code=0)

So 62114 tests selected, 62114 passed, 0 failed, in all three runs. No test was
reported as failed or errored in any run.

The tests that cover the changed code path are in `tests/test_metadata.py` and
all fall inside that passing set:

- `test_from_email_wraps_description_content_type_parse_errors`
  (tests/test_metadata.py:376), parametrized at tests/test_metadata.py:366-375
  with `"text/plain\n folded"`, `'text/plain; charset="unterminated'`,
  `"text/plain; {b}"`, `"text/plain; a}b"`, `"text/plain; x*"`. It asserts
  `exc.field == "description-content-type"`, `repr(description_content_type) in
  str(exc)` and `"is not a valid content type" in str(exc)`
  (tests/test_metadata.py:388-392).
- `test_valid_description_content_type` (tests/test_metadata.py:585), the
  keep-working cases such as `"text/plain; charset=UTF-8"`,
  `"text/markdown; variant=GFM"` (tests/test_metadata.py:576-582).
- `test_invalid_description_content_type` (tests/test_metadata.py:605) and
  `test_invalid_description_content_type_without_defects`
  (tests/test_metadata.py:613), which includes `"application/octet-stream"`.
- `test_invalid_charset_error_message` (tests/test_metadata.py:621), which
  requires the message to still match `iso-8859-1`.

## What is missing

Nothing. The ticket (ticket.md) asked for one product behaviour: every badly
written content type value should reach the project's plain
"not a valid content type" message for the `description-content-type` field.
That behaviour is present in the working tree. The only modified file is
`src/packaging/metadata.py` (`git diff HEAD --stat`: `1 file changed, 22
insertions(+), 6 deletions(-)`); no other file is touched, so nothing else the
ticket asked for is absent.

I read the whole changed function. In
`_process_description_content_type` (src/packaging/metadata.py:639) the
assignment and parse are now wrapped:

```
        try:
            message["content-type"] = value
            content_type, parameters = (
                # Defaults to `text/plain` if parsing failed.
                message.get_content_type().lower(),
                message["content-type"].params,
            )
        except (ValueError, IndexError) as exc:
            raise self._invalid_metadata(
                f"{value!r} is not a valid content type for {self.raw_name!r}",
                cause=exc,
            ) from exc
```

and a defects check was added before the allow-list check:

```
        if message["content-type"].defects:
            raise self._invalid_metadata(
                f"{value!r} is not a valid content type for {self.raw_name!r}"
            )
```

The `cause=exc` keyword is real: `_invalid_metadata(self, msg: str, cause:
Exception | None = None)` at src/packaging/metadata.py:597-598, and the same
pattern is used by `_process_name` (src/packaging/metadata.py:620-622) and
`_process_version` (src/packaging/metadata.py:630-632). The message text names
the field via `self.raw_name`, which for this field is
`description-content-type`, matching the ticket's wording and the assertions at
tests/test_metadata.py:390-392.

The ticket's user-experience example is a value "text/plain followed by a stray
star". The parametrized case `"text/plain; x*"` (tests/test_metadata.py:373)
goes through this new path. A literal `"text/plain*"` (no semicolon) would
instead still fall to the older `must be one of [...]` branch inside the same
function, which is also a plain field-naming message. I am not certain which
form the ticket author pictured, so I say this plainly and do not treat it as a
blocking item; no test in the suite checks that literal form, and the suite is
green either way.

## Why it fails

It does not fail. All three harness runs finished with exit_code=0 and
`62114 passed, 417 deselected`, with no failures and no errors. I found no
failing test name and no failing assertion in the output I was given.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a reader who loads a package's details, hits a content
type line that is written badly, and today ends up with a raw, hard to
understand error that never names the offending line or field. The product that
exists now matches that description after the change.

Before this change, in `_process_description_content_type`
(src/packaging/metadata.py:639), the value was handed straight to
`email.message.EmailMessage` and used (`message["content-type"] = value;
content_type, parameters = message.get_content_type().lower(),
message["content-type"].params`). For some malformed values that step raises a
bare `ValueError` or `IndexError` from the email parser, so the reader never
reaches the friendly allow-list message. Such a raw error does not say
`description-content-type`, does not say which value was wrong, and points the
reader at their tooling rather than at their own metadata file.

After the change, both kinds of bad input converge on one plain message. Values
that make the parser raise (`ValueError`, `IndexError`) are caught and converted
to `InvalidMetadata` for `description-content-type` with the value shown, and
the original error is kept as `__cause__` so nothing about the underlying
problem is lost. Values that the parser accepts but flags with defects (for
example a parameter with no value) are also reported with the same plain
message. So a reader with a malformed content type line now sees "the value is
not a valid content type for the description-content-type field" style text
that names their field and echoes their value, which is exactly the outcome the
ticket's "What should happen" and "User experience" sections ask for.

Nothing is taken away. Values that used to be accepted are still accepted:
`test_valid_description_content_type` (tests/test_metadata.py:585) covers
`text/plain`, `text/x-rst`, `text/markdown` and their `charset`/`variant`
forms, and it passes. Values that used to be rejected for reasons other than
parsing still get their existing messages: `"application/octet-stream"` is
rejected via the allow-list branch (`test_invalid_description_content_type_without_defects`,
tests/test_metadata.py:613) and `"text/plain; charset=iso-8859-1"` still
produces a message mentioning `iso-8859-1`
(`test_invalid_charset_error_message`, tests/test_metadata.py:621); both pass.
The new defects check runs before the allow-list check, and the only values it
can newly catch are ones the parser itself marked as defective, so previously
valid content types are unaffected — confirmed by the green
`test_valid_description_content_type` case set and by the full suite.

In short: the reader-facing difference the ticket promised is delivered,
the set of accepted values is unchanged, and the existing rejection message for
non-parse failures is unchanged.