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
  other history.
- Failing tests may already exist in the workspace. They are locked and
  cannot be modified. They define what "done" means.
- The dependencies currently installed match the manifests in the tree; if
  the ticket implies a new dependency, prefer what is already installed.
- The documents in this existing codebase do not include any changes or information about what this ticket asks for. Nothing here already implements it.

## Rules
- Every command output you report must be real. Never invent or simulate
  output. If a command fails, report the failure as it happened.
- Never claim a test passes without running it.
- The seeded QA tests are read-only (locked). If a test blocks you, work with
  the product code until it passes; never edit the tests.
- Work only inside this workspace. Do not touch anything outside it.
