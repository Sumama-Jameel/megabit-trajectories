# Saving and reading back an option with no default breaks with a confusing error

## What happens now

Click uses one special marker object to mean "this option or argument has no value set". Today, if I save an option that has no default to a file (or send it over a network connection) and read it back, the reading fails with an error that says an object is not a valid Sentinel. The same thing happens for an argument with no default. The marker also loses its identity in other kinds of copying.

## What should happen

I should be able to save an option, an argument or a whole command, read it back later, and find that the "not set" marker is still the exact same single marker click uses everywhere. The same should hold when I make a plain copy or a full deep copy of any of these.

## About this project

Click is a Python library for building command line programs. You describe your options and arguments with decorators, and click handles reading the values, showing help text, and reporting errors for you. Its change log at the top of the project records every user-visible change in each release.

## Problem this solves

Some people keep their click commands in a cache file, a task queue, or any other place where objects are saved and reloaded. With the current version, a command with an option that has no default cannot be reloaded at all, so caching or shipping commands is simply not possible without a painful workaround.

## What changed

The "not set" marker now survives being copied, being fully copied, and being saved to a file and read back. Reloading an option or an argument that has no default gives back the very same marker object, and comparing it against click's marker still says they are the same thing. A new entry was added at the top of the change log for the next release describing this.

## Impact

Correctness and compatibility. Code that saves and reloads click commands keeps working instead of failing with a confusing error.

## User experience

Before: I save a command that has an option with no default, then read it back. Instead of getting my command, I get an error telling me an object is not a valid Sentinel, and the command is lost.

After: I save the same command and read it back. The command comes back intact, and its option with no default still reports as not set, the same as click's own marker.

## Hints

- /workspace/src/click/_utils.py
- /workspace/tests/test_utils/test_sentinel.py
- /workspace/CHANGES.md
- /workspace/src/click/core.py
