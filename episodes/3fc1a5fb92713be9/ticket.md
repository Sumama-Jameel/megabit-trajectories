# The error message changes the value I typed

## What happens now
When my package details are read and one value is not accepted, the message I get back does not always show my value the way I wrote it. A value that has a curly-bracket marker in it gets that part swapped out for the field name. For a bad version written that way, the message ends up naming the field in place of my value, so the text I am told about is not the text in my file.

## What should happen
The message should repeat my value exactly as I typed it, and it should still tell me which field is at fault. Then I can see the actual text that was refused and go fix it.

## About this project
This project is a Python library for reading and checking package metadata, the small text that describes a package such as its name, version, and required packages. Tools use it to open that text and to report when a value does not fit the rules.

## Problem this solves
When the message rewrites my value, I cannot tell which text the tool objected to. I am left with an error that does not match my file, so I cannot work out what to correct.

## What changed
The message now quotes the value I typed, unchanged, and names the field separately. The old behavior, where my value was re-read as if it were part of the tool's own wording, is gone. This covers the messages that quote a bad value, such as the ones for the name, the version, extra names, the required Python version, and the required package lines.

## Impact
Ease of use: error messages say what I actually typed.

## User experience
Before: I put a value with a curly-bracket marker into the version field by mistake, and the message told me the field name was invalid for the field name, which made no sense. After: the same mistake gives a message that repeats my value as typed and says it is not a valid version, so I know exactly what to correct.

## Hints
- /workspace/src/packaging/metadata.py
- /workspace/tests/test_metadata.py