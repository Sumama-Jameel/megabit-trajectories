# Feedback report

## Tests

The harness ran the Diff2 suite three times with `python -m pytest` in `/workspace`
(rootdir `/workspace`, configfile `pyproject.toml`, testpaths `tests`). All three runs
matched, and this is the only test evidence I quote — I did not run any command to
produce it.

- Run 1: `exit_code=0`, `62410 passed, 427 deselected in 128.09s (0:02:08)`
- Run 2: `exit_code=0`, `62410 passed, 427 deselected in 139.59s (0:02:19)`
- Run 3: `exit_code=0`, `62410 passed, 427 deselected in 153.45s (0:02:33)`

Inventory line from that output: `collected 62837 items / 427 deselected / 62410 selected`.
So 62410 tests passed, 0 failed, 0 errored, three runs in a row. The captured output is
truncated in the middle by the harness, so I cannot read per-file counts for
`tests/test_tags.py`; the run summary at the end is complete and reports zero failures.
No test failure is reported, so there is nothing to explain in "Why it fails".

## What is missing

Nothing from the ticket is missing. The change (from `git diff --stat HEAD`) touches
exactly three files: `CHANGELOG.rst | 2 ++`, `docs/tags.rst | 2 ++`,
`src/packaging/tags.py | 28 ++++++++++++++++++++++++++++`.

- Ask "I can ask for only the pure-Python tags ... the same answer on every computer":
  present. `src/packaging/tags.py:617` defines
  `def pure_python_tags(python_version: PythonVersion | None = None) -> Iterator[Tag]`
  and its body yields only `Tag(version, "none", "any")` for each version in
  `_py_interpreter_range(python_version)` (`tags.py:648-649`). The docstring says these
  tags "do not depend on the running interpreter's ABI or platform, so the result is the
  same on every computer" (`tags.py:626-627`). No platform lookup happens in the function.
- Ask "give it a version I choose or let it use the version of the running Python":
  present. `tags.py:643-644`: `if python_version is None: python_version =
  sys.version_info[:2]`. The docstring documents this default (`tags.py:631-632`).
- Ask "if I give it a version with nothing in it, ... a clear message telling me the
  version must have at least one item": present. `tags.py:645-646`:
  `if not python_version: raise ValueError("python_version must contain at least one
  item")`. Documented as `:raises ValueError: If **python_version** is an empty sequence.`
  (`tags.py:633`).
- Ask "the tags page of the documentation now shows it next to the other low-level
  helpers": present. `docs/tags.rst:101` adds `.. autofunction:: pure_python_tags`,
  placed right after `.. autofunction:: generic_tags` (`docs/tags.rst:99`).
- Ask "the wider helper that also looks at the running computer now gets its portable
  part from this same place, so the two stay in step": present.
  `src/packaging/tags.py:614`, the tail of `compatible_tags`, is now
  `yield from pure_python_tags(python_version)`, replacing the inline loop.
- Ask "Nothing was taken away": consistent with the evidence. `compatible_tags` still
  builds the platform-tied `none` tags and the interpreter `none-any` tag before it
  delegates (`tags.py:610-614`), so its output content and order are unchanged, and the
  full suite passes.
- The ticket's "What happens now" complaint that "nothing in the tests mentions it" no
  longer holds: `tests/test_tags.py:1512` defines `class TestPurePythonTags` with cases at
  `:1514` (chosen version), `:1524` (`(3,)` major-only), `:1528` (empty tuple raises),
  `:1532` (default), and `:1544` together with the `pytest.fail(...)` guard at `:1542`
  ("pure_python_tags() queried the running platform"), which covers the "same on every
  computer" claim.
- `"pure_python_tags"` is added to `__all__` (`tags.py:49`), so it is a normal public name.
- The changelog bullet was added: `CHANGELOG.rst` adds "Add
  :func:`~packaging.tags.pure_python_tags` to generate only the platform-independent
  ``py*-none-any`` tags." That bullet carries no `(:issue:...)`/`(:pull:...)` reference
  while its neighbours do. The ticket did not ask for a changelog entry at all, so this is
  a cosmetic note, not missing work. Likewise `.. versionadded:: 26.3` (`tags.py:635`)
  matches `__version__ = "26.3.dev0"`; no issue.

## Why it fails

No test fails. All three harness runs ended with `exit_code=0` and
`62410 passed, 427 deselected`, so there is no failing test to explain.

## Verdict

VERDICT: approve

## Experience difference

Before this change, a user who wanted only the portable tags had no direct name for
them. The only low-level entry points shown on the tags page were `generic_tags`,
`compatible_tags`, `mac_platforms` and similar helpers, and the portable set was buried
inside `compatible_tags`, which first probes the running machine. Calling it returned a
long list mixing interpreter-version `none` tags, the machine's OS tags such as
`manylinux`/`macosx`/`win_amd64`, the interpreter `none-any` tag, and finally the
`py*-none-any` entries, so the user had to filter that list by hand and got a different
answer on different computers. There was also no way to pass a Python version of the
user's choosing, and passing an empty version produced an unclear failure from the inner
helper.

Now, after the change, `packaging.tags.pure_python_tags` exists and is public (listed in
`__all__`). Calling it with nothing returns the same short portable list on every
computer, containing only `<python>-none-any` entries (`py3`, `py2`-style ranges derived
from the running interpreter's major/minor version, defaulting to
`sys.version_info[:2]`). Calling it with a version sequence such as `(3, 3)` or `(3,)`
returns exactly that version's portable entries, so the user controls the answer. The
function never touches the platform, so it cannot report anything about the machine it
runs on. Calling it with an empty sequence raises a `ValueError` whose message says
`python_version must contain at least one item`, and that error is named in the
docstring. The tags documentation page now lists the helper through
`.. autofunction:: pure_python_tags`, next to `generic_tags`, so the user can find it;
its docstring on that page states the generated pattern `py*-none-any`, the version
default, the versionadded marker, and the `ValueError` case. `compatible_tags` keeps
working exactly as before but now takes its trailing portable block from the same
function, so the two helpers cannot drift apart: whatever version the user passes to
`compatible_tags` is forwarded to `pure_python_tags` (`tags.py:614`). Nothing was removed:
all previously produced tags are still produced, `generic_tags` and the other helpers are
untouched, and the whole suite still passes three times over.