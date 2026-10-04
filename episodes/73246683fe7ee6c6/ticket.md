# The decorator that builds the extra class methods has no readable name

## What happens now
If you open the file that builds the extra class methods, the one thing that attaches the printed form, the equality check, the hash and the initializer is called with a single letter. Nothing in the file says in words what that piece does, and the name that spells it out is not used anywhere in the project. The single letter is also what that file exports, which makes it hard to tell which name is meant for use inside the project and which name is meant for people writing their own classes.

## What should happen
The file that builds the extra class methods should carry that piece under a name that says in words that it adds those methods to your class. The short one-letter name should still be handed out by the package, so every existing use of it keeps working exactly as before.

## About this project
This is the attrs project, a small helper library for Python. You write down the fields your class should have and it creates the initializer, the printed form, the equality check and the hash for you, so you do not have to write those by hand.

## Problem this solves
Reading the source of the package today gives no hint about what the one-letter decorator does, so anyone trying to understand or reuse it has to read the whole body. Giving it a readable name inside the package removes that guesswork without asking anyone to change the code they already wrote.

## What changed
The decorator that attaches the extra methods now lives in the internal file under a spelled-out name instead of the single letter. The package still exports the short single-letter name for everyone who uses it from the top level, and nothing was removed: the same switches for the initializer, the printed form, equality and hashing all behave as before.

## Impact
Readability and naming inside the project. No speed change, no behavior change for people writing classes, and no change to the short name or to the four switches that turn the extra methods on and off.

## User experience
Before: you decorate your class with the short single-letter name, it works, and nothing about your code changes. But if you go into the package source to see what that single letter does, you find no readable name for it anywhere.

After: your code stays exactly as it was and keeps working the same way. The single letter still comes from the top level of the package. Inside the package source, the piece that adds the methods is now named in words, so you can tell at a glance what it does. The only thing that stops working is reaching into the internal file for the single letter, since that file now uses the readable name.

## Hints
- /workspace/attr/_make.py
- /workspace/attr/__init__.py
- /workspace/tests/test_make.py
- /workspace/tests/test_funcs.py
