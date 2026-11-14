# Class-level keyword-only setting overrides my own and inherited field choices

## What happens now
When I mark a class as keyword-only and one of its own fields asks to stay positional, that field still gets forced to become a keyword-only argument. Fields that come from a parent class get forced the same way, so a parent's required field is pulled out of the position my callers already use.

## What should happen
The class setting should only cover fields written in that class. A field that asks to stay positional should stay positional, and fields coming from a parent class should keep the order and style they already had. I also want a way to bring back the wide behavior when I truly want every field in the family to be keyword-only.

## About this project
attrs is a Python library that helps people define plain data-holding classes with far less typing. It writes the setup code for you, including how a class is built, compared, and displayed. Many projects use it to keep their class definitions short and consistent.

## Problem this solves
When a parent class has a required field, turning that field into a keyword-only argument breaks the order callers rely on and makes the child class awkward to use. I need my parent's setup left untouched while only my own new fields become keyword-only.

## What changed
Previously, marking a class as keyword-only turned every field into a keyword-only argument, including fields from parent classes and fields that asked to stay positional. Now the class setting only applies to the fields written in that class, a field asking to stay positional stays positional, and inherited fields keep the style they had. So you get two new results: the setting is narrower than before, and an extra flag lets you ask for the old wide behavior when you need it. The keyword setting on a single field also accepts an empty choice that means follow the class.

## Impact
Ease of use and compatibility for classes that mix positional and keyword-only fields.

## User experience
Before: I wrote a parent class with one required positional field and a child class marked keyword-only, and the parent's field was pushed into a keyword-only argument, so every caller had to name it. After: the parent's field stays positional, only my new child fields are keyword-only, and my callers keep the order they already used.

## Hints
- /workspace/src/attr/_make.py
- /workspace/src/attr/_next_gen.py
- /workspace/src/attr/__init__.pyi
- /workspace/src/attrs/__init__.pyi
- /workspace/tests/test_make.py
