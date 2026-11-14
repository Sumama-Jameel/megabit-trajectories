# Broken metadata files report only the first kind of problem, and repeat one field twice

## What happens now

When I hand the library a metadata file that contains a line it cannot read (an unknown field, or a required field written twice), it stops there. The report I get has the single word "unparsed" as its heading and one complaint about that one line. The rest of the file is never checked, so a missing name, a missing version and a missing metadata version are all left out of the answer, and I cannot tell how bad the file really is. When the unreadable line is a required field, the field is both listed as unreadable and reported as missing, so the same field shows up twice in one report.

## What should happen

Reading a metadata file should give me one complete report: every problem in the file, whether the line was unreadable or the value inside it was wrong, gathered into a single list. A field should be mentioned once, not once as unreadable and again as missing, and a file that has no problems should still be returned normally.

## About this project

This is a small library of helpers for Python packaging: it knows how to compare and sort versions, check version ranges, clean up package names, and recognise platform tags. It also reads the metadata block that a package carries, such as its name, version and dependencies, so that tools installing or inspecting packages can trust what they read.

## Problem this solves

When a package's metadata file is broken, the answer I get is partial and confusing: some problems are listed and the most important ones, a missing name or version, can be left out entirely. I end up fixing the file one error at a time, and I cannot tell from the report whether the file is slightly wrong or badly wrong.

## What changed

- Reading a metadata file now collects every problem into one report, instead of stopping after the first group of problems it finds.
- Missing required fields are always listed, even when something else in the file could not be read.
- A field whose content could not be read is mentioned once, and is no longer also reported as missing.
- Every such report now uses the same heading wording, "invalid or unparsed metadata", instead of the shorter "unparsed".
- Nothing changed for a metadata file that is complete and correct: it is still returned as before, with no complaint.

## Impact

Correctness and ease of use of the error messages. Only the reporting of broken metadata is affected; valid metadata is read exactly as before.

## User experience

Before: I give the library a metadata file with one unknown line and a valid name and version. I get a report whose heading is "unparsed" and which lists only that unknown line, and the metadata version that the file never declared is not mentioned at all. After: the same input gives me one report whose heading is "invalid or unparsed metadata" and which names the unknown line together with the missing metadata version, name and version, so I can see the whole state of the file at once.

## Hints

- /workspace/src/packaging/metadata.py — the Metadata reading entry point, the invalid-metadata error type and the field name mapping it relies on
- /workspace/src/packaging/errors.py — the helper that gathers several complaints and raises them together
- /workspace/tests/test_metadata.py — the existing expectations for reading metadata from email
- /workspace/docs/metadata.rst — the user documentation for reading metadata
