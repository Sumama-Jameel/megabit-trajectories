# I want each field to carry its own check on the value

## What happens now

An attribute I declare can hold a name, a default value, or a way to build a default value. There is no place on the attribute to say what the value has to look like. If I want to catch a bad value, I have to write my own initializer by hand, check the values myself after they arrive, and repeat that for every class. Bad objects exist in my program until something else trips over them later.

## What should happen

I should be able to attach a check to a field when I declare it. When I create an object, the check runs on the value that is handed in, before the value is stored, and if the check raises, no object is created and the error comes straight back to me.

## About this project

This project is a small library called attrs. It writes the repetitive parts of a class for you — the initializer, the comparison methods, the printed form, and the hash — based on the list of fields you give it.

## Problem this solves

Right now a wrong value is only noticed when something downstream reads the field and breaks, and the report points at the wrong place. I need the bad value to be refused at the moment the object is made, at the spot I declared the field, so the error tells me the true cause.

## What changed

- Every field can now carry a check on its value, set where I declare the field.
- The check runs while the object is being created, before the value is stored, and the object is not produced when the check raises.
- The printed list of fields now shows the check for each field, so the listing I get from the library tells me which field guards its value and which one does not.
- The story page about the project's history now uses the current name of the library everywhere instead of the older name.

## Impact

Ease of use and correctness. Classes I write get shorter because the value check travels with the field instead of living in a method I write myself, and wrong values stop earlier.

## User experience

Today: I list my fields, write my own initializer, and check each value myself after it is stored, so a wrong value slips through and only shows up much later when something else uses it.

After: I list my fields and give the ones that need it a check. When I try to create an object with a value the check rejects, I get the error right away from the object creation itself, and the object is never handed back to me.

## Hints

- /workspace/attr/_make.py
- /workspace/attr/_dunders.py
- /workspace/attr/__init__.py
- /workspace/docs/api.rst
- /workspace/docs/why.rst
- /workspace/tests/test_dunders.py
- /workspace/tests/test_dark_magic.py