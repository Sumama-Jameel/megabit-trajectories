# I have no way to ask "is this one of my classes?" without catching an error

## What happens now

Today the library gives me two tools: one that lists the field names of a class, and one that turns an object into a plain dictionary. The listing tool shouts with an error when the class was not created with this library at all. So when I want to know whether a class is one of mine, the only thing I can do is call the listing tool and wrap it in my own error handling every time, or look at an internal marker on the class myself.

## What should happen

I should be able to hand any class to a single question and get a plain yes or no back, with no error raised when the answer is no. It should say yes for a class made with this library, and no for anything else, including ordinary classes such as the built-in object class.

## About this project

This project is a small library for describing classes in a short way instead of writing out all the usual boilerplate by hand. When you mark a class with its decorator, the library builds the initializer, the comparison, and the text form for you, and gives you small helpers for working with the result.

## Problem this solves

I keep writing the same try and except block just to find out whether a class came from this library. Without a direct yes or no answer, checking a class before I use it costs extra lines, is easy to get wrong, and turns a simple check into an error path.

## What changed

A new question-asking tool now sits next to the field listing and dictionary helpers. It returns yes for a decorated class, including one that declares no fields at all, and returns no for a class that was not decorated, such as the plain object class. It never raises an error. The new tool is also listed in the names the library exports, so it can be reached the same way as the two existing helpers. Nothing that worked before stops working.

## Impact

Ease of use, and no change in how existing code behaves. The new tool does no work beyond looking at a class, so speed is unaffected.

## User experience

Before: I want to check whether a class is one of mine, so I call the field listing tool. If the class came from somewhere else, an error is raised and I have to catch it, which means every call site needs its own error handling.

After: I ask the new question and get no back, quietly, with nothing to catch. If the class is one of mine, I get yes and can go straight on to listing its fields.

## Hints

- /workspace/attr/_funcs.py
- /workspace/attr/__init__.py
- /workspace/tests/test_funcs.py
