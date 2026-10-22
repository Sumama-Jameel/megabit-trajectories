# I cannot choose the text my program prints for --version

## What happens now
When I run my program with the --version flag, the line it prints is fixed. It only fills in the program name, the package name, and the version number. There is no ready-made option that lets me print anything else, for example the path of the program file or the Python version in use.

## What should happen
A new ready-made option is available that I can attach to my command. I give it a small piece of my own logic, and that logic receives the current run context and hands back the exact text to print. When a user runs the long version flag or the short version flag, my text is printed and the program stops.

## About this project
Click is a helper library for building command-line programs in Python. It provides ready-made pieces such as a version option and a help option, so the author of a program does not have to build those pieces from scratch.

## Problem this solves
People who ship command-line tools often need the version line to carry more than a bare number, because that number alone does not tell a user which copy of the tool is running or what environment it is running in. Without a supported way to supply that text, the author has to fight the built-in option instead of just printing what they need.

## What changed
Previously the only ready-made way to print a version line was the built-in version option, and its text was limited to three values. Now there is a second ready-made option I can reach for, that takes my own logic and prints whatever text I hand back for both the long and the short version flag. The built-in version option keeps working the same way for everyone already using it, but the set of values it fills in is now fixed.

## Impact
Ease of use, with a supported and correct way to print my own version text.

## User experience
Before: I run my program with --version and get only the package name and the number, which does not tell me which build or which Python is in use, and I have no supported way to print more. After: I attach the new option, give it my own text, and running --version prints exactly what I want and then exits.

## Hints
- /workspace/src/click/decorators.py
- /workspace/src/click/__init__.py
- /workspace/docs/api.md
- /workspace/tests/test_basic.py
- /workspace/CHANGES.md
