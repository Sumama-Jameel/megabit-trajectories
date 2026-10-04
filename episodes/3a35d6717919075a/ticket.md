# The names inside the project do not match the names the documentation shows

## What happens now

Inside the project, the two things everyone uses — the marker that describes one attribute and the class decorator that describes a whole class — are written with the private-looking underscore names everywhere: in the class-building module, in the checks module, and in the project's own test files. So when I read the documentation and then look at the code that ships with the project, the words never match.

## What should happen

The project should write those two names the same public way everywhere inside it, exactly as the documentation already shows them, so the words I read in the documentation are the words I see in the project.

## About this project

attrs is a small library for describing data classes. You list the attributes a class should have, and the library writes the setup, the printed form, the equality check and the hashing for you. It also ships with ready-made checks for attribute values, like "must be a number" or "must be a list of numbers".

## Problem this solves

I want to trust that what the documentation shows me is what the project really uses. Right now I cannot copy a name from the documentation and find that exact word anywhere in the code that comes with the library, which makes verifying the documentation slow and confusing.

## What changed

Only the words used inside the project. The two main names are now written the short public way throughout, and the two short shortcuts people already use stay exactly as they are. Nothing that worked before stops working, and no name a user relies on disappears.

## Impact

Readability and naming only. No behaviour change, no removal of anything a user can already do.

## User experience

Today I write my class with the decorator and the attribute marker, and my program works. Afterwards I write the very same example with the very same words and I get the very same result. The only difference is that the words now match what the documentation told me from the start.

## Hints

- /workspace/attr/_make.py
- /workspace/attr/__init__.py
- /workspace/attr/validators.py
- /workspace/tests/test_make.py
- /workspace/tests/test_funcs.py
