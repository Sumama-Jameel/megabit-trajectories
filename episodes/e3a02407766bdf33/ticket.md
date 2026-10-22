# Asking for no wheels still hands me the wheel built for my own machine

## What happens now
When I ask a lock file to give me packages and I pass an empty list of wheel tags to mean "no wheels allowed", that empty list is treated the same as handing over no tags at all. The tool then falls back to the tags of my own machine and offers me the wheel that was built for my machine, even though I asked for the opposite. The help text for this step only says that tags are used when they are left out, yet an empty list gets the very same treatment.

## What should happen
When I pass an empty list of tags, I should truly get no wheels. If the lock file has a source package, I should get that source package. If the lock file carries only wheels, I should get a clear error that says no wheel matched and no source package is available. Only when I leave the tags out entirely should my machine's tags be used.

## About this project
This project is a Python library that reads and works with package lock files, the files that record exactly which package files a project needs. It helps other tools pick the right package files for a given computer and Python setup, and it can complain when nothing suitable is present.

## Problem this solves
I need to be able to force the source package, or to check what happens when no wheel fits my machine. Today I cannot do that, because an empty list of tags is ignored and my machine's wheel comes back instead. This hides real problems in a lock file, such as a lock file that holds no source package at all.

## What changed
An empty list of tags now means "no wheels allowed" instead of "no preference". The source package is selected when one is present, even if a wheel for my machine is also listed. When only wheels exist, I get a message that no wheel matched and no source package is available. Leaving the tags out entirely still uses my machine's tags, just as before.

## Impact
Correctness and ease of use.

## User experience
Before: I ask for no wheels by passing an empty list of tags, and I still get the wheel built for my machine. After: I ask for no wheels the same way, and I get the source package, or a clear message telling me that there is no wheel and no source package when the lock file has none.

## Hints
- /workspace/src/packaging/pylock.py
- /workspace/tests/test_pylock_select.py
