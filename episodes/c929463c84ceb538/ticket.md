# One command cannot run another command

## What happens now
If one command tries to run a second, complete command from inside itself, the run fails with a confusing message about an object not being iterable. The helper that does this has no idea it was handed a whole command, so it tries to treat it like a plain function. There is also no way to hand over the option values you have already collected, so every value would have to be typed out again.

## What should happen
Calling a full command from inside a running command should just work, and the values passed in should arrive at that command. There should also be a way to call the other command while reusing the values already collected for the current command's options. If the thing handed over is not a command, the user should get a short, clear complaint instead of a crash.

## About this project
Click is a library for building command line programs in Python. A program is made of commands, each with its own options and arguments, and groups that bundle commands together under one name. Click reads what the user typed on the command line and hands it to your code.

## Problem this solves
Many tools need one command to reuse the work of another, such as a hidden command that does the real work while both the group command and a subcommand call it. Today people hit an unhelpful failure, or they hand every option value over by hand one by one, which is easy to get wrong and tedious to maintain.

## What changed
Running another command from inside a command now works and passes the values through. A new way to call another command reuses the values already collected for the current command's options instead of asking for them again. If a command has no function attached, or if a plain function is handed to the new reusing way, the user gets a clear message saying what was wrong.

## Impact
Ease of use, and clearer error messages.

## User experience
Before: a group command that runs a second command with the number 42 stops with a message about an integer not being iterable, and the user has no clear idea why. After: the same call prints 42, and the second command can be run without repeating values that were already given.

## Hints
- /workspace/click/core.py
- /workspace/docs/commands.rst
- /workspace/tests/test_basic.py
- /workspace/tests/conftest.py