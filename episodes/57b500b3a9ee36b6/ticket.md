# Subcommands stop with an error unless the outer command builds the shared object first

## What happens now

When I give my subcommands a shared object through the pass decorator, every subcommand refuses to run unless some outer command built that object first. Calling a subcommand on its own stops with the message about a context object of that type not existing, so a command I can see in my help text cannot actually be run by itself.

## What should happen

I want to tell the pass decorator to build the object for me when it is missing. Then a subcommand that is run on its own still works, using a fresh empty object, and an outer command can still set values on the same object for its subcommands to use.

## About this project

This project is Click, a Python library for building command line programs. You describe your commands with decorators, and Click takes care of parsing options, printing help, and passing values into your functions.

## Problem this solves

Without a way to have the object created on demand, every command in a group has to repeat the same setup code, and the subcommands are unusable unless the user happens to call the top level command in the right order. That makes help text misleading and forces me to keep the setup in sync across every command.

## What changed

Two things users can do now that they could not before. First, the running command's context can be asked for an object of a given type and will hand back a newly created empty one when nothing of that type has been stored yet, instead of only returning objects that already exist. Second, the pass decorator factory takes an extra switch that turns on that behavior, so a decorated command runs on its own rather than stopping with the "Managed to invoke callback without a context object of type ... existing" error. Commands that do not turn the switch on keep the exact same behavior and the exact same error message as before, so nothing changes for anyone already relying on the old error. The tutorial in the documentation also grows an "Ensuring Objects" section, and its example object can now be created with no values at all, so the standalone example in that section actually runs.

## Impact

Ease of use, with no change for existing programs.

## User experience

Before: I run my subcommand directly and get an error saying no context object of that type exists, and the only way around it is to build the object myself in every parent command. After: I turn on one switch on my subcommand, running it directly works and uses an empty object, and when I run it through the top level command it uses the object my top level command filled in.

## Hints

- /workspace/click/core.py
- /workspace/click/decorators.py
- /workspace/docs/complex.rst
