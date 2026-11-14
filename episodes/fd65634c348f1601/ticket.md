# Only options and arguments can carry help text; every other kind of parameter cannot

## What happens now

If you write your own kind of parameter, you cannot give it a help text. Passing one raises an unexpected keyword argument error, the settings dictionary of a custom parameter has no help entry at all, and options and arguments each handle the help text on their own instead of sharing it.

## What should happen

Every kind of parameter should accept the same help value, clean up the indentation of a multi-line help text, add the deprecation label when the parameter is marked as no longer recommended, and report its help text in the settings dictionary.

## About this project

Click is a Python library for building command line programs. You describe your options, arguments and commands, and Click turns them into a program that parses input, prints help screens, and reports errors nicely.

## Problem this solves

When you add a parameter of your own to a command, it shows up without any description while every option and argument beside it has one. You have no way to give it help text, so users see an unexplained entry in the help screen and in the settings dictionary.

## What changed

Help text now lives on the shared parent of all parameters instead of being handled twice, once for options and once for arguments. Options and arguments keep working exactly as before, including trimming extra indentation from a multi-line help text and adding the deprecation label. The extra help argument accepted directly by the options and the arguments no longer applies, so passing it there raises an error like any unknown name. Version 8.5.1 is noted as the release where this applies.

## Impact

Usability and consistency: custom parameters can finally carry a description, and all kinds of parameter behave the same way.

## User experience

Before: you write a parameter of your own, try to give it a help text, and the program stops with an unexpected keyword argument error; the settings dictionary you read to build documentation has no help entry for it, so the parameter appears bare.

After: you give your parameter the same help value you give an option, and it is accepted, its multi-line indentation is tidied up, the deprecation label is added when you mark it as no longer recommended, and the help text shows up in the settings dictionary alongside the other parameters.

## Hints

- /workspace/src/click/core.py
- /workspace/tests/test_info_dict.py
- /workspace/CHANGES.md