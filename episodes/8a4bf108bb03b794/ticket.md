# A marker or requirement that ends with a line break is accepted without complaint

## What happens now
When I give the library a marker or a package requirement that ends with a line break, it accepts the text and gives me a result. It does not tell me that the text is not valid. I ran the current code with a marker and a requirement that each ended with a line break, and both were accepted with no error.

## What should happen
When the text ends with a line break, I should get the normal error that says the input is not valid. When the text ends with ordinary spaces or tabs, it should still be accepted and treated as if those spaces and tabs were not there.

## About this project
This project is a Python library for working with Python package metadata. It reads and checks things like version numbers, package requirements, and environment markers. Many other tools use it to decide which packages to install and how to compare their versions.

## Problem this solves
When a stray line break sneaks into a requirement or a marker, for example one copied out of a file, the library accepts it silently. That hides the mistake and makes it hard to find where the bad text came from.

## What changed
A marker or a requirement that ends with a line break is now reported as an error instead of being accepted. Trailing spaces and tabs are still accepted and ignored, just as they are today.

## Impact
Correctness and ease of use.

## User experience
Before, I pass a requirement that ends with a line break and it is accepted, so I never notice the stray break. After, the same text gives me an error, so I can spot and fix the extra line break right away.

## Hints
- /workspace/src/packaging/_tokenizer.py
- /workspace/tests/test_markers.py
- /workspace/tests/test_requirements.py
