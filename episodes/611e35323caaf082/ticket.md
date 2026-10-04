# The printed form of my classes puts angle brackets around the name

## What happens now

When I look at an object in the console or in a debugger, the text the library builds for me has angle brackets wrapped around the class name and its values. A class holding x and y shows up as <C(x=1, y=2)>, and a class with no values at all shows up as <C3()>. Those brackets add noise right next to the name, and the examples on the front page and in the guide on why you would use the library all show that same bracketed form.

## What should happen

The text for an object should show the class name and its values plainly, with no angle brackets. The same object should appear as C(x=1, y=2), and the class with no values should appear as C3(). The front page and the guide should show the plain form too, so the words match what I actually see.

## About this project

attrs is a Python package whose decorators write the repetitive parts of a class for you. You list the values your data class holds, and the library writes the starter, the comparison, the hash, and a readable printed form for that class.

## Problem this solves

The brackets make every printed object clutter, and the project's own guide says they add ambiguity when you are trying to read a value while debugging. I want to look at an object and read a plain name and a list of values, with nothing extra around the name.

## What changed

Objects made with this library now print their class name and values without the surrounding angle brackets. The front page example and the guide on why you would use the library were updated to show the plain form, including the hand-written comparison example in the guide. The bracketed form is no longer produced by the library at all.

## Impact

This is a visible change in usability: the printed form of every class the library builds loses the brackets. Anything you compare against that text, such as saved output, examples in your own notes, or a check in your own test suite, has to expect the plain form. The values, the comparisons, the hash, and the starter are untouched.

## User experience

Before: I create a class with x and y, make an object with the values 1 and 2, and print it. I see <C(x=1, y=2)>, and a class with nothing in it prints as <C3()>. After: the exact same code gives C(x=1, y=2), and the empty class gives C3(). The name and the values are all that remain on the line.

## Hints

- /workspace/attr/_dunders.py
- /workspace/README.rst
- /workspace/docs/why.rst
- /workspace/tests/test_dunders.py
- /workspace/tests/test_make.py
