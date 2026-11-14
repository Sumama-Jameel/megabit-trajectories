# The "finished call" log line breaks when the finish time is unknown

## What happens now
When a retried call finishes, the built-in after-log helper writes a line saying what finished, how long it took, and how many times it was tried. That helper reads the time since the call started. If that time is missing, the helper still tries to show it as a number, which fails. The user gets an error instead of a log line.

## What should happen
When the time since the call started is missing, the line should still be written. It should show a question mark where the number of seconds normally goes, and keep the rest of the words the same, including the call name and the number of tries.

## About this project
This project is a small Python library that reruns a piece of work when it fails, waiting a bit between tries. It also lets people log a line each time a try finishes, so they can watch what happened. Many apps use it to make shaky network calls more reliable.

## Problem this solves
People who watch their logs want every finished try to leave a line. When the finish time is missing, the whole line disappears and an error shows up instead, right when the person is trying to find out what happened.

## What changed
The line now copes with a missing finish time. Where the number of seconds was forced into the words before, the line now shows a question mark instead of failing. A new check covers this missing-time case. The wording of the line for normal runs stays the same.

## Impact
Fewer errors and easier log reading.

## User experience
Before: a call finishes without a recorded finish time, and asking for the finished-call line raises an error, so nothing is written. After: the same call writes the line with a question mark where the seconds would be, showing the call name, the question mark, and which try number it was.

## Hints
- /workspace/tenacity/after.py
- /workspace/tenacity/__init__.py
- /workspace/tests/test_after.py
