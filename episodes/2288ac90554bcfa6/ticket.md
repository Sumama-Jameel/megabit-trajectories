# Writing metadata fails when a field has a carriage return, and a two-line summary is accepted

## What happens now

When I build metadata text and any field, such as an author name, contains a carriage return or another kind of line break, the writing step stops with an error saying the header contains a newline. Only the plain newline gets the space added that lets a long field continue on the next line. At the same time, the check on the summary field only looks for a plain newline, so a summary holding a bare carriage return is accepted and handed back unchanged, even though it really is two lines.

## What should happen

Every kind of line break that counts as a line separator should be handled the same way when metadata text is written: the field continues on the next line with a space in front, instead of the write failing. And the summary field should be rejected whenever it holds any of those line breaks, so a "one line" summary really is one line.

## About this project

This project is a Python library that reads and writes package metadata: the information that describes a Python package, such as its name, version, author, and summary. Other tools, including installers and package indexes, rely on it to turn that information into text and read it back again.

## Problem this solves

My build input comes from Windows machines, where a line break is stored as a carriage return followed by a newline, and a stray carriage return can survive on its own. Today I cannot produce metadata text at all for such input, and a summary that silently contains two lines slips past the rule that says it must be a single line, so tools reading my output get something different from what I declared.

## What changed

Metadata text can now be written when a field contains a carriage return, a form feed, a line separator, a paragraph separator, a group separator, a file separator, a record separator, a unit separator, or the next-line character; the value is folded onto the next line with a space added, rather than the write stopping with an error. Setting a field on a metadata message directly behaves the same way. The summary check now rejects all of those line breaks with the existing "summary must be a single line" message, not just the plain newline. Nothing that worked before stops working; values that already contained only a plain newline are written exactly as they were.

## Impact

Ease of use and correctness of the written output.

## User experience

Before: I set an author name that came from a Windows file and it contains a line break, I ask the library to give me the metadata as text, and I get an error about a folded header containing a newline, so I cannot produce my output. After: the same request succeeds and the author line is written as two lines, the second one starting with a space, which tools read as one continuous field. And a summary with a bare carriage return now gives me the "summary must be a single line" error instead of quietly passing through as two lines.

## Hints

- `/workspace/src/packaging/metadata.py`
- `/workspace/tests/test_metadata.py`
- `/workspace/CHANGELOG.rst`
