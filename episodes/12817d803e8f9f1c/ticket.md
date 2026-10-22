# A bad dependency entry hides the other problems in the same group

## What happens now
When a group of extra dependencies in a project file holds an entry that is not a valid dependency, reading that group stops at that entry. The user sees only that one complaint. Any other problems found in the same group before it are thrown away, and the user never sees the message that says the group data was malformed.

## What should happen
When a group holds an entry that is not a valid dependency, the user should get one report that says the group data was malformed and lists every problem found in that group, including the bad entry and any others found at the same time.

## About this project
This project is a library that other Python tools use to read and understand project files. It reads the declared dependencies, the version ranges, and the named groups of extra dependencies that a project may define. Its job is to hand back a clean list of what to install, or a clear message when the project file does not make sense.

## Problem this solves
When one bad entry hides the other problems, the user has to fix one mistake, run the tool again, and repeat until the file is clean. Seeing all the problems for a group in one report lets them fix everything in a single pass.

## What changed
An entry that is not a valid dependency is now reported together with the other problems found in the same group, instead of stopping the report on its own. The message that names the group as malformed is now shown for this case too. Nothing else about reading a group behaves differently.

## Impact
Clearer error messages, ease of use, and fewer repeated runs to clean up a project file.

## User experience
Before: a user has a group with one empty item and one text entry that is not a valid dependency, and runs the tool on that group. They get only the complaint about the bad text entry, and the empty item problem is lost. They fix the text entry, run again, and only then see the empty item problem. After: the very same run gives one report that names the group as malformed and shows both problems together, so they can fix both at once.

## Hints
- /workspace/src/packaging/dependency_groups.py
- /workspace/src/packaging/errors.py
- /workspace/tests/test_dependency_groups.py
