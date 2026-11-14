# No built-in way to check that a value provides a zope interface

## What happens now
The only built-in check you can attach to an attribute is the one that verifies a value is an instance of a given type. There is no built-in check for a zope.interface interface, so if your attribute must carry an interface, you have to write a checking function yourself and pass it in by hand. The documentation lists only the type check, and the example page shows only the type check, so there is no working sample to copy. The library that provides interfaces is also not listed among the packages the check runs install, and the setup file points the run command at a test file name that is not in the project.

## What should happen
You should be able to attach a built-in check to an attribute that verifies the value provides a given zope interface, and get a clear error when it does not. The example page should show a short runnable sample of that check, and the documentation should list it next to the existing type check. Running the checks from an installed copy should work with the folder that actually holds them.

## About this project
This is a small library for writing Python classes with less repetition. You list your attributes once, and the library builds the class for you, including the usual object behavior and the option to check each value when it is set.

## Problem this solves
Without a built-in interface check, every class of mine that holds an interface has to carry a hand-written checking function that I copy from file to file. I want the same one-line way the type check already works.

## What changed
The library now ships a second ready-made check that verifies a value provides a named zope interface, and it is a full sibling of the type check with the same behavior and the same error message style. The documentation page for the checks now lists both, and the examples page adds a runnable sample showing the error when a value is missing the interface and the acceptance when it has it. The packaging files now name the folder that holds the checks for the run command, and list the interface library so the checks can run.

## Impact
Ease of use, plus the packaging of the check run.

## User experience
Today, to require an interface on an attribute I write my own checking function and repeat it in every class that needs it. After this, I ask for the built-in interface check by giving it the interface I care about, and the value is accepted or a clear error is raised right away, the same way the type check behaves today.

## Hints
- /workspace/attr/validators.py
- /workspace/docs/api.rst
- /workspace/docs/examples.rst
- /workspace/tests/test_validators.py
- /workspace/setup.py
- /workspace/tox.ini
