# The message I get when I try to change a frozen object is shared and not my own

## What happens now

When I try to change a value on an object that was made frozen, the error text is
stored just once on the error type itself. Every error of that kind points at the
same, changeable list of words instead of carrying its own message. Because it is a
list, someone can change it in one place and every error in the whole program shows
the changed words. So when I catch the error, reading the message off it is not
dependable, and matching that text is not dependable either.

## What should happen

After the change, each error raised when I try to change a frozen object carries its
own fixed copy of the text. The words I read off the caught error are the same words
as its first argument, and they say that the attribute cannot be set. Each error
stands on its own, so changing one can never change any other. I can catch the error
and read or match its message without surprises.

## About this project

This project is a library called attrs. It helps people build classes that hold data,
with much less typing than writing them by hand. One of its features is "frozen",
which locks an object after it is created so nobody can change it afterwards. When
someone does try to change a frozen object, the library raises an error that explains
what went wrong.

## Problem this solves

People who catch the error from changing a frozen object cannot trust the message
they get, because the same text is shared by every error and can be changed in one
place. They need the text on each caught error to belong to that error alone, so
reading it or matching it always gives the same, correct answer.

## What changed

The error raised when changing a frozen object now sets its own message when it is
created. The message on the caught error equals its first argument and says that the
attribute cannot be set. The old shared, changeable list of words is gone, so one
error can no longer affect the message seen on another. Everything else about how
frozen objects behave stays the same.

## Impact

Correctness and ease of use when handling errors from frozen objects.

## User experience

Before: I change a value on a frozen object, catch the error, and its message comes
from one shared, changeable list, so the text is not reliably mine. After: I change a
value on a frozen object, catch the error, and it shows its own fixed message saying
the attribute cannot be set, and that same text is its first argument.

## Hints

- /workspace/src/attr/exceptions.py
- /workspace/src/attr/exceptions.pyi
- /workspace/src/attr/setters.py
- /workspace/src/attr/_make.py
- /workspace/tests/test_functional.py