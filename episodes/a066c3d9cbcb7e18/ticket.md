# My check function cannot tell which field it is checking

## What happens now
When I attach a check function to an attribute, the generated start-up code hands that function only the value I passed in. The function has no idea which attribute it is looking at, so it cannot use the attribute's name, type, or default, and it cannot say which field was wrong in its error message.

## What should happen
A check function should be handed the attribute it is checking together with the value, so I can write one function, use it on many fields, and have the error message name the field that failed.

## About this project
This is a small library for writing plain data classes with much less typing. You list your attributes once, and the library writes the start-up method, the text form, equality, and the value checks for you.

## Problem this solves
Today I have to write a separate copy of the same check for every single field, because the check only receives a value and cannot say which field it came from. My error messages just show a number, so when a class fails to start up I have to search the whole program to find out which value was bad.

## What changed
The start-up method that the library writes now passes the attribute description and the value into every check function, in that order. A check function written for the old way, taking a single value, will now be called with an extra argument and will stop working unless it accepts more than one argument.

## Impact
Ease of use and correctness of error messages. It touches every attribute that carries a check function, and check functions that take only the value need adjusting.

## User experience
Before: my check function takes the value, and the error it raises carries just the value 42 with no field name. After: the same check function is handed the attribute description first and the value 42 second, and the raised error carries both, so I can put the field name into the message the user sees.

## Hints
- /workspace/attr/_dunders.py
- /workspace/tests/test_dunders.py
