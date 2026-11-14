# Briefing

You are working in a real git repository. Your goal is set by the ticket you
are told to read; this briefing explains how to work.

## How to work
1. Read this briefing fully.
2. Read the ticket file (its exact path is in your opening prompt).
3. Read the hints file (its exact path is in your opening prompt) if one was
   provided — it lists the areas of the codebase the ticket relates to.
4. Explore the codebase with read/glob/grep until you understand the areas
   the ticket touches.
5. Plan first. Then implement. Then run the project's tests yourself and
   iterate until they pass.

## Facts about this environment
- The repository is at a single commit named "Initial state". There is no
  other history. git log, git diff, and git status are useless — do not run
  them.
- Failing tests may already exist in the workspace. They define what "done"
  means.
- Those tests are LOCKED by the harness: never create, modify, or delete
  any file under tests/ (adding a new test counts as modifying them). The
  harness refuses such writes, and any change that gets through deletes
  this episode. Make the code satisfy the tests — never the reverse.
- The dependencies currently installed match the manifests in the tree;
  prefer what is already installed, but do not hesitate to install
  dependencies if they are required or needed.
- The documents in this existing codebase do not include any changes or information about what this ticket asks for. Nothing here already implements it.

## Rules
- Every command output you report must be real. Never invent or simulate
  output. If a command fails, report the failure as it happened.
- Never claim a test passes without running it.
- If a seeded QA test blocks you, work with the product code until it
  passes.

## How to run tests
Use this command to run the project's tests:

  python -m pytest 

Replace `{args}` with the test path or filter you need (e.g., `tests/test_foo.py` or `-k test_name`). When you have finished your change, run the full suite and confirm every test passes — including the seeded QA tests in the workspace.
