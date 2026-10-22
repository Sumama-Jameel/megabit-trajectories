# Old helper names for streams give no warning

## What happens now
Right now the two helpers that give a program a stream for reading and writing live in the click.utils module under the plain names get_binary_stream and get_text_stream. They look like normal, everyday names, and the same plain names are also shown straight from the main click module. When someone reaches for either of these names, nothing tells them the name is old and is going away in Click 9.0. Some of the other old names in click.utils do warn, but these two stay silent.

## What should happen
When someone reaches for the old get_binary_stream or get_text_stream name, either from the main click module or from the click.utils module, that person should see a clear message saying the name is old and will be removed in Click 9.0.

## About this project
This project is a toolkit for building command line programs in Python. It helps people handle arguments, options, prompts, output, and files, so they can focus on what their program does. Many people build their own tools on top of it, so the names it offers them matter.

## Problem this solves
People cannot tell that these two helper names are on their way out, so their scripts keep using names that will one day disappear. A clear message lets them move to the current names before that happens.

## What changed
The two helpers now have names that start with an underscore, so they no longer look like everyday names. The part of click.utils that answers for old names now also answers for get_binary_stream and get_text_stream and gives the same kind of old-name message. The wording used for the other old names in that same place now matches this wording. The documentation sentence about closing files that are opened only when used is reworded.

## Impact
Ease of use and a clearer path when upgrading.

## User experience
Before: a person writes a small program and reaches for the old get_binary_stream name from click; the program runs with no message at all, so the person has no idea the name is old. After: the same person uses that old name and sees a message saying it is old and will be removed in Click 9.0, so they know to switch to the current name.

## Hints
- /workspace/src/click/utils.py
- /workspace/src/click/__init__.py
- /workspace/tests/test_testing.py
- /workspace/docs/api.md
- /workspace/docs/wincmd.md
- /workspace/docs/handling-files.md
- /workspace/CHANGES.md
