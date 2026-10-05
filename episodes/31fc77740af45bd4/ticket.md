# attrs.fields() refuses to look at an object, only at its class

## What happens now

Today, asking attrs to list the fields of one of your objects fails. Only the class is accepted. I ran it in the current version with a plain object that was made with attrs, and with an ordinary empty object, and both times I got an error saying the thing I passed must be a class. So when a made object arrives from somewhere else, I have to fetch its type myself before I can ask what fields it has, and my editor's type checker marks that call as wrong.

## What should happen

I should be able to hand a made object straight to attrs and get back the list of its fields, with the same result as when I pass the class it was made from. When I pass something that is neither a class nor a made object, I should still get an error, and the message should say that both classes and made objects are accepted.

## About this project

attrs is a Python library for writing classes that store their data clearly, with less repetitive typing than writing everything out by hand. It offers one way to find out what fields a class or object has, and it can check those fields against a given set of types.

## Problem this solves

Very often I only have the object, not the class, in my hands — for example a record that was read from a database, a message that came off a queue, or a value built by another library. Having to go back to its type is an extra step, and because the editor believes only classes are allowed, it shows a warning on correct, working code.

## What changed

attrs now accepts a made object anywhere it accepts a class, and it returns the field list for that object's class. The wording of the error for other kinds of things now names both classes and made objects, so the message says what is actually allowed. The example in the documentation shows that the object and the class give the same answer. The editor's description of what is accepted was widened to match, so the type checker no longer complains. What gets removed is the current expectation in the test suite that a made object must be rejected.

## Impact

Ease of use, plus one friendlier error message. Nothing that works today changes its result.

## User experience

Before: I load a made object from somewhere, hand it to attrs to see its fields, and get an error telling me the thing must be a class, while my editor underlines the same line.

After: I hand the same object over and get back the full list of its fields, exactly as if I had passed the class, and the editor stays quiet.

## Hints

- /workspace/src/attr/_make.py
- /workspace/src/attr/__init__.pyi
- /workspace/docs/api.rst
- /workspace/tests/test_make.py
- /workspace/tests/test_mypy.yml
