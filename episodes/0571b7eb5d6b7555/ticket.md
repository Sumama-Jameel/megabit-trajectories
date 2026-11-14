# Listing attributes works on instances by accident, and nothing is written down about the helpers

## What happens now

When I ask for the attributes of an object, the tool accepts an object as well as a class and silently switches to the object's class. When the class has no attrs fields at all, the error it raises is the wrong one: it says the thing I passed was the wrong type, when the real issue is that the class carries no fields. Asking whether something is an attrs class behaves the same loose way. On top of that, there is no written explanation anywhere: the documentation page has nothing but a title, and the helpers, the single-attribute helper, the class decorator, and the attribute information object all have no descriptions of what their arguments do.

## What should happen

Asking for the attributes of a class gives a clear error if I pass an object instead of a class, and gives a separate, clear error if the class has no fields. Asking whether a class is an attrs class gives a simple yes or no for classes. The attribute listing can be turned into a plain dictionary, including nested dictionaries when the fields point at other attrs classes. Every helper, every argument, and every returned field carries a written explanation, and all of it also appears on the documentation page.

## About this project

This is a small library for describing classes with less repetition. You list the fields of a class once and the library builds the class for you, including its text form, its equality, its hash, and the way new objects are created, with switches to turn each of those off.

## Problem this solves

Because the tool accepts an object where a class was meant, a mistake in my own code passes silently and I get results about something other than what I asked for. And since nothing is written down, I cannot tell which of my classes are attrs classes without running them and reading the source.

## What changed

Listing attributes now refuses objects and points at the class instead, and reports a missing-fields problem with its own error rather than the type error. The yes-or-no check is documented for classes and follows the same rule. Turning a value into a dictionary walks the fields and nests dictionaries when a field points at another attrs class. The attribute information object is now available from the main package entry point next to the other helpers, so I can get at it without reaching into a private module. Every helper, argument, switch, and returned field is described in writing, and the documentation page now has a full reference with runnable examples.

## Impact

Correctness of errors, ease of use, and documentation.

## User experience

Before: I pass an object where I meant a class, and the listing quietly answers for the object's class, so I never find out I made a mistake. And the documentation page is empty, so I cannot learn the rules from reading.

After: I pass an object where I meant a class and I get told straight away that a class is needed. I pass a plain class with no fields and I get told the class has no fields. The documentation page now shows every helper with its arguments and runnable examples.

## Hints

- /workspace/attr/_funcs.py
- /workspace/attr/__init__.py
- /workspace/attr/_make.py
- /workspace/docs/api.rst
- /workspace/tests/test_funcs.py