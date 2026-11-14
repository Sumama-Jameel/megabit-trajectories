# Editors do not know a path option gives me a real path object

## What happens now
When I ask for a path option that hands me a pathlib Path, I still get a red squiggle under the value, because nothing tells my editor what the value really is. The path type only says "str or bytes or anything path-like", so every use of the value looks uncertain. I also cannot write down the type myself, because asking for it directly, like naming Path with pathlib.Path in square brackets, fails right away with an error saying Path is not a generic class.

## What should happen
When I choose a specific path type for an option, my editor and type checker should know the value is exactly that kind of object, everywhere the value appears: on the command, in a prompt, and when I use the type directly. I should also be able to name the path type myself in square brackets without getting an error.

## About this project
Click is a Python library for writing command line programs. You describe commands, options and arguments with short readable pieces of code, and Click turns them into a program with help text, checking of values, and prompts. It also makes sure your program's behaviour is clearly described to editors and type checkers.

## Problem this solves
I write command line tools where a path option is documented and checked as a pathlib Path, yet my editor keeps reporting the result as an unknown mix of text and paths. That pushes me to add casts and extra checks that the program does not need, which hides real mistakes.

## What changed
A path option can now record the one path type it produces, and that specific type is reported to editors and type checkers. If you do not choose a path type, the value is still reported the same way as before, as text, bytes or something path-like. If you choose text, the value is reported as text. If you choose a pathlib Path, the value is reported as a pathlib Path. Naming the path type yourself in square brackets now works and keeps that single type. Nothing about what your program does at runtime changes.

## Impact
Ease of use and correctness: the reported type now matches the value that is really handed back.

## User experience
Before: I write an option that gives me a pathlib Path, and my editor says the result might be a string or bytes, so I add a manual conversion to keep it quiet. After: I write the same option, and my editor says the result is a pathlib Path, so I use it directly with no extra conversion.

## Hints
- /workspace/src/click/types.py
- /workspace/tests/test_types/test_Path.py
- /workspace/tests/typing
- /workspace/CHANGES.md
