# A number in the pre-release letter spot crashes instead of telling me what is wrong

## What happens now
When I build a version and put a number where the small pre-release letter belongs, the toolbox stops with a confusing message about a missing text feature instead of telling me my input is wrong. The same rough edge shows up when I swap out the pre-release piece of an existing version.

## What should happen
The toolbox should tell me plainly that the pre-release part needs a letter such as a, b, or rc followed by a whole number, the same way it already does for every other kind of wrong input.

## About this project
This project is a toolbox that other Python programs use to read, compare, and work with software version numbers such as 1.2.3. It also lets people build a version out of its separate parts, including the plain numbers, the pre-release piece, and the final-release piece.

## Problem this solves
When my input is wrong, I get a scary technical stop instead of a plain message, so I cannot tell what I typed wrong or how to fix it.

## What changed
A number placed where the pre-release letter belongs now produces the normal invalid-version message. Before, that same input stopped with a missing text feature message. Every valid version keeps working exactly as it did.

## Impact
Correctness and ease of use.

## User experience
Before: I build a version with release 1 and a pre-release part written as the number 1 and the number 1, and the toolbox stops with a confusing message about a missing text feature. After: I try the same thing and the toolbox tells me the pre-release part needs a letter like a, b, or rc followed by a whole number.

## Hints
- /workspace/src/packaging/version.py
- /workspace/tests/test_version.py