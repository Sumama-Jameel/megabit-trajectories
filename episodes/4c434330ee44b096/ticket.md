# Fields with underscores can only be set by typing the underscore

## What happens now
When I declare a field whose name has a leading or a trailing underscore, the setup method that the library writes for me accepts only the name with the underscores still attached. So every time I build the object, I have to type the underscore in the keyword myself.

## What should happen
I should be able to pass the value under the plain name, with the surrounding underscores left off, whether they sit at the start of the field name, at the end, or at both ends. The field on the object should still carry its full underscored name, and the printed form should still show the underscores.

## About this project
This is a small library for Python that writes simple data classes for you. You list your fields on a few lines, and the library gives you a setup method, a readable printed form, comparisons, and value checks, so you do not write that repetitive code by hand.

## Problem this solves
Today every place that creates the object has to repeat the underscores, which is noisy and easy to slip up on. Letting me drop them at the call site makes building the object read like ordinary code and keeps the naming of my fields to one place.

## What changed
The setup method the library writes now takes each field under the name with leading and trailing underscores removed. Fields that have a plain value, a made-on-demand value, or a value check are all set through that same short name. Nothing was taken away: the stored field and the printed form keep the underscored name, and field names written without any underscores behave exactly as they did before.

## Impact
Ease of use at the call site. Stored values and printed output stay the same, and existing field names without underscores are untouched.

## User experience
Before: I declare a field whose name starts with an underscore, and the only way to build the object is to pass the same underscored keyword, so every call site carries the underscore along. After: I pass the plain short name when I build the object, the value lands on the underscored field, and the object still prints with its underscored name.

## Hints
- /workspace/attr/_dunders.py
- /workspace/attr/_make.py
- /workspace/docs/examples.rst
- /workspace/tests/test_dunders.py
- /workspace/tests/test_dark_magic.py
