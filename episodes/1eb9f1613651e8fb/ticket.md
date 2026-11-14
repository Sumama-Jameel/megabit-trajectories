# Turning my objects into dictionaries is slower than it needs to be

## What happens now
When I ask the library to turn one of my objects into a dictionary, it works, but the
work is slower than it should be. I do this a lot, on objects that hold many values,
and the wait adds up. There is also no check that keeps unusual value types intact
when the object is turned into a dictionary.

## What should happen
I keep calling the same thing the same way, and the dictionary I get back is the same
one I got before, with the same keys, the same values, and the same types inside.
The result arrives a lot faster.

## About this project
This project is a small helper library for people who write classes whose main job is
to hold data. Instead of writing the boring parts by hand, I describe my class once and
the library writes the rest for me. One of the things it offers is turning an object
into a plain dictionary.

## Problem this solves
Converting objects into dictionaries is a common step when sending data somewhere else,
like saving it or passing it along. When that step is slow, my whole program feels slow,
and there is nothing I can change in my own code to make it quicker.

## What changed
Turning an object into a dictionary now gives the exact same dictionary as before, only
much faster. Plain values and lists, sets, and dictionaries inside it still come out the
same shape. Values whose type is a plain number or text type are kept as they are, and
this is now checked with a test so it stays true.

## Impact
Speed, with no change to the results.

## User experience
Before: I turn a large object into a dictionary and sit and wait longer than I want,
several times in a row. After: I make the exact same call and get the exact same
dictionary back in a fraction of the time.

## Hints
- /workspace/src/attr/_funcs.py
- /workspace/tests/test_funcs.py
