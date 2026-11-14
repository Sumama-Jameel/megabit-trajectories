# The field helper has a name that is too short to understand

## What happens now
Today the only way to mark a field on a class is to use a helper whose name is just the single letter "a". When I read that name, I cannot tell what it means or what it does. The examples in the readme also use that short name, and the "why" page shows examples from a different library instead of showing how this project's own classes look.

## What should happen
I should be able to mark a field using a helper with a clear name, "ib", and the readme and the "why" page should show examples that use that clear name so I can copy them and understand them right away.

## About this project
This project helps people write small classes that hold data. It lets a person say which fields a class has, and then the project fills in the boring parts, like setting values in the right order and printing the class nicely. It is meant to remove the repetitive typing that comes with plain data-holding classes.

## Problem this solves
When the name of the field helper is a single letter, a reader cannot guess what it means, so the code and the examples are hard to follow. A clearer name makes the project's own examples readable and lets people copy them without confusion.

## What changed
The field helper is now offered under the name "ib" instead of the single letter "a". The readme examples and the "why" page examples now use that clearer name, and the "why" page now shows this project's own classes instead of another library's classes.

## Impact
Ease of use and clarity for anyone reading the examples or writing their own classes.

## User experience
Before: I open the readme, see the helper written as "a", and cannot tell what it does or why it is there. After: I open the readme, see the helper written as "ib", and understand at a glance that it marks a field on my class.

## Hints
- /workspace/attr/__init__.py
- /workspace/attr/_make.py
- /workspace/README.rst
- /workspace/docs/why.rst
- /workspace/tests/test_dark_magic.py
