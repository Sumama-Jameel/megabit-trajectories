# Tests cannot be run on Python 3

## What happens now

On Python 3 the test run fails before a single test runs, because the test helper imports a text-buffer module that exists only on Python 2. The helper also walks the settings dictionary with a Python-2-only call, and it checks the typed-in text against the Python-2 text name, so on Python 3 the typed-in text is never prepared correctly and the captured output is a text stream even though the helper reads it as bytes.

## What should happen

Running the test suite on Python 3 should work the same way it works on Python 2: typed-in text is turned into bytes only when it is not already bytes, the input and the captured output are handled as bytes with a UTF-8 text wrapper on Python 3, and the settings dictionary is walked in the way that Python 3 expects.

## About this project

Click is a Python library for writing command line programs. It gives you short ways to declare options, arguments, and prompts, and it prints the help text for your program. The repository also carries a copy of the standard optparse module inside it.

## Problem this solves

Without this, nobody working on Click on a current Python can tell whether their change broke anything, because the whole suite errors out during setup. The project's own notes say the tests need to run on Python 3 as well.

## What changed

The test helper now picks its buffer class based on the Python version, so Python 3 gets a byte buffer and a UTF-8 text wrapper while Python 2 keeps what it had. The typed-in text check no longer refers to the Python-2-only text name, and the settings dictionary is walked with a small helper that works on both. The file example test now opens its example file for writing and reading text rather than bytes, so reading the file back returns text on Python 3. The license file also now credits the optparse author and the Python software foundation for the optparse code shipped inside the project.

## Impact

Compatibility. The suite runs on Python 3 as well as Python 2, and the file example test reads back what it wrote.

## User experience

Before: running the tests on Python 3 stops during setup with an import error about a missing text-buffer module, and no test result is produced. After: the same command runs the whole suite on Python 3 and reports pass or fail for each test.

## Hints

- /workspace/tests/conftest.py
- /workspace/tests/test_basic.py
- /workspace/LICENSE
