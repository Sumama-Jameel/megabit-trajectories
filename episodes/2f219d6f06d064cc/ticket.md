# A list of checks cannot be used for the list itself or for dictionary keys and values

## What happens now

The check that looks inside a list accepts a group of checks side by side, but only for the items in that list. The rule for the list itself, and all the rules for a dictionary (the keys, the values, and the dictionary as a whole), take exactly one rule each. If I pass two rules in one of those places, the class refuses to be created with an error saying that value must be callable. My editor also warns me before I even run anything, because the hints for those places only describe a single rule.

## What should happen

I should be able to write checks as a list or a tuple wherever one is accepted, including the list itself and the keys, values and whole dictionary. All of the checks I list then run, and every one of them has to be happy for the value to be accepted. My editor should accept the same lists without a warning.

## About this project

attrs is a Python library that writes plain classes for me so I do not have to write the repetitive parts myself. Those classes can carry rules that run whenever a value is set, such as "this has to be a number" or "the keys here have to be text". Two of those rules look inside a collection and check what is inside it.

## Problem this solves

Rules for a list or a dictionary usually come in pairs, such as "has to be a list" together with "must not be empty". Because each place only takes one rule today, I have to build the joined rule by hand every single time, which is easy to get wrong and easy to forget.

## What changed

The list check now takes a list or a tuple of checks both for its items and for the list itself. The dictionary check now takes a list or a tuple for its keys, its values, and the dictionary as a whole. In each case the listed checks are joined into one rule that runs them all, so nothing is taken away and every rule still has to pass. The built-in help for these two checks now says that one or more checks can be given, and notes the behaviour as of version 25.4.0. The hints my editor uses were widened to match. Nothing was removed.

## Impact

Ease of use and correctness of the collection checks, with nothing taken away.

## User experience

Before: I want a field to hold a list that is not empty, so I pass "has to be a list" as the list rule and then join it by hand with "must not be empty" into one rule of my own, repeated in every class that needs it. Passing both in one go fails and the class is not created.

After: I list both checks next to each other in the same call, in order. The value is accepted only when both hold, and an empty list is refused with a message that points at my list. The same works for a dictionary field where I want to require both keys and values.

## Hints

- src/attr/validators.py
- src/attr/validators.pyi
- tests/test_validators.py
- tests/typing_example.py
- changelog.d
