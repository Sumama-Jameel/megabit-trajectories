# Turning attrs objects into tuples is slower than it needs to be

## What happens now
When I turn an attrs object into a tuple, each value in it is put through a long
chain of checks. Plain values such as numbers and text cannot match most of
those checks, so the effort is wasted. The other helper that turns an object
into a dictionary already passes over plain values early and leaves them alone,
but the helper that builds a tuple does not.

## What should happen
Plain values should be noticed straight away and skipped past the extra checks,
so the same tuple comes back faster. The values, their order, and their types
should stay just as they are today.

## About this project
attrs is a small helper library for Python. It lets people write short classes
that hold data, without repeating the same setup code again and again. One of
its helpers turns such an object into a tuple of its values.

## Problem this solves
People who turn many objects, or objects with many fields, into tuples wait
longer than needed for a result they already know how to get. A common habit is
to run that conversion in a loop, so the wasted effort adds up.

## What changed
The tuple helper now spots plain values early, the same way the dictionary
helper already does. Values, their order, and their types come back the same.
The choices for how collections are handled behave the same as before. What
goes up is the speed of the conversion.

## Impact
Speed, with no change to the result.

## User experience
Before, a loop that builds tuples from thousands of objects takes a while, and
there is no way to make it quicker. After, the same loop finishes sooner, and
every tuple it hands back is the same as before.

## Hints
- /workspace/src/attr/_funcs.py
- /workspace/tests/test_funcs.py