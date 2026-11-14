# A lock file that lists no allowed environments is not taken seriously

## What happens now

A lock file can name the environments it is meant for. That list sits in a
place called environments. Today, when that list is empty, the program skips
the check that compares the list with my environment. It treats an empty list
the same way it treats a lock file that says nothing about environments at all.
So a lock file that on purpose says "no environment is allowed" behaves as if
it allows every environment, and I get packages back with no warning.

## What should happen

When a lock file lists environments but the list is empty, no environment can
match it. I should get the clear error message that says my environment does
not satisfy any of the environments named in the lock file. When a lock file
says nothing about environments, then nothing should be restricted and I should
get my packages as before.

## About this project

This project is a set of tools for reading information about Python packages.
One of the things it reads is a lock file, which records exactly which
packages and versions belong to a project. People use these files to get the
same packages every time, on the machines they choose.

## Problem this solves

When a lock file deliberately allows no environments, I cannot trust it,
because the file is quietly ignored and I still get packages. I need the tools
to respect what the file says, so that a lock file with no allowed
environments fails loudly instead of silently handing me a result.

## What changed

An empty list of allowed environments in a lock file is now treated as a real
restriction, not as if the list were absent. The old behavior, where an empty
list simply let every environment through, is gone. A lock file that does not
mention environments at all keeps working the same way as before, with no
restriction.

## Impact

Correctness and trust in lock files.

## User experience

Before: I point the tool at a lock file whose list of allowed environments is
empty, and it returns packages for my machine as if the list did not matter.
After: I point the tool at that same lock file and get the error that my
environment does not satisfy any of the environments named in the lock file.
A lock file with no list at all still returns my packages.

## Hints

- /workspace/src/packaging/pylock.py
- /workspace/tests/test_pylock_select.py
