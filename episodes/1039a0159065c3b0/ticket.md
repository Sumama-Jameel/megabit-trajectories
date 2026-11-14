# A broken content type line makes reading a project's details fail with a confusing error

## What happens now
When I read a project's details and the line that says what kind of text the long description is (the content type line) is written badly, the read can end with a raw, hard to understand error. Today the reader at src/packaging/metadata.py takes that line and uses it right away with no safety check. It only looks at the result afterwards to decide if the content type is one of the allowed ones, such as text/plain, text/x-rst or text/markdown. If the text is malformed in certain ways, it never gets to that friendly message, and I am left with an error that does not tell me which line is wrong or why.

## What should happen
When the content type line is not a proper content type, I should see the project's own clear message that says the value is not a valid content type for the description-content-type field. Every badly written value should reach that same plain message, no matter how it is broken.

## About this project
This is a library that reads and writes the details that travel with a Python package, such as its name, version and long description. The details are stored in a small text format, and the library turns that text into something programs can read and check. It also tells the person reading a package's details, in plain words, when one of those details is not written the way the format expects.

## Problem this solves
When a package's details contain a badly written content type line, I cannot tell what is actually wrong, so I struggle to fix my package and I might think my tools are broken. A clear message that points at the content type value tells me exactly what to correct.

## What changed
Broken content type values now lead to the same plain message the project already uses for other bad values, and the message names the description-content-type field. Values that are already treated as invalid keep being reported the same way, and values that are fine keep working exactly as before. Content type values that were accepted before are still accepted. Nothing is taken away.

## Impact
Ease of use and clearer error messages.

## User experience
Before: I read a package whose details say the description is text/plain followed by a stray star, and the read ends with an unexpected error that does not explain the content type line. After: I read the same package and get a plain message that says the value is not a valid content type for the description-content-type field, so I know right away what to fix.

## Hints
- /workspace/src/packaging/metadata.py
- /workspace/tests/test_metadata.py