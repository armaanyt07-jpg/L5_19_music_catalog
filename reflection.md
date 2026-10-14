# Lab 5: Reflection

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the style and readability issues from Flake8 and Pylint. These were the long lines (E501/C0301), the one-line `if` (E701/C0321), the variable named `l` (E741), the extra `else` after `return` (R1705), the camelCase function names (C0103) and the missing docstrings. Each one came with an exact line number and a clear rule, and fixing it did not change what the program does. Renaming the functions only needed care to update every call site.

**Hardest:** the issues where I had to understand the behaviour, not just the rule.

- **Mutable default argument (`playlist=[]`).** The fix is short, but I had to understand why it is a bug. The default list is created once, when the function is defined, and every call that leaves out `playlist` shares it. I had to check that `main()` still built the same playlist after changing the default to `None`.
- **Replacing `pickle`.** Bandit only says "pickle is unsafe". I had to choose a safe replacement. I used JSON because a playlist is just a list of strings, and I had to confirm that `save_playlist` and `load_playlist` still round-trip correctly.
- **The bare `except:`.** I needed to decide which exception is actually expected (`sqlite3.Error`). While doing that, I noticed that `SUM()` returns `NULL` (`None`) on an empty table. No tool reported this; I only found it by thinking about edge cases.
- **SQL injection.** Pylint's message on the same line (C0209, "use an f-string") pointed the wrong way. An f-string would have kept the injection. The correct fix was a parameterised query, which made both warnings go away.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes. Bandit **B311** flagged `random.choice(ids)` in `shufflePick()` and warned that "standard pseudo-random generators are not suitable for security/cryptographic purposes." That is true in general, but here the random number only picks the next song for shuffle play. It is not used for passwords, tokens, session IDs or anything else an attacker could exploit. Switching to `secrets.choice` would add nothing. So I kept `random` and suppressed the warning with `# nosec B311`, plus a comment explaining why, so a future reader can see that this was a deliberate decision and not a hidden warning.

A related case is Pylint **C0209** (consider using an f-string) on the SQL line. It is not exactly a false positive, but following its advice would have been harmful, because the real problem on that line was SQL injection, and that needs placeholders, not a different way of formatting strings. This showed me that tool suggestions need human judgement.

Also, Bandit **B403** (importing `pickle`) only warns about the import. On its own it is not a vulnerability. The danger is calling `pickle.loads` on untrusted data, which is what B301 points to.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **In the editor:** run Pylint and Flake8 through the IDE (for example, the VS Code Python extension) so problems are underlined while I type and are fixed straight away.
- **Pre-commit hooks:** use the `pre-commit` framework to run Flake8, Pylint and Bandit (plus a formatter like Black) on changed files before each commit, so obvious problems never get into the repository.
- **CI pipeline:** add a GitHub Actions workflow that runs all three tools on every push and pull request. The build fails on any Bandit Medium/High finding, on any Flake8 error, or if the Pylint score drops below a threshold (for example `pylint --fail-under=9.5`). Saving the reports as build artifacts makes it easy to see trends over time.
- **Shared config:** keep the tool settings (`.pylintrc` or `pyproject.toml`, `.flake8`, Bandit settings) in the repo so the whole team runs the same rules. Agree on line length so Flake8 (79) and Pylint (100) do not disagree.
- **Handling false positives:** suppress a warning only inline (`# nosec B311`, `# pylint: disable=...`), always with a reason, and review these suppressions during code review instead of switching rules off globally.
- **Alongside tests, not instead of them:** static analysis did not catch the empty-catalog crash or the `None` total. Unit tests for edge cases (an empty catalog, titles with quotes) are still needed.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Measured results:** the Pylint score went from **4.57/10 to 10.00/10**. Bandit went from **4 issues (2 Medium, 2 Low) to 0**. Flake8 went from **7 issues to 0**.
- **Security:** song titles and artists are now passed as query parameters, so SQL injection is no longer possible. Before, a normal title like "Don't Stop" crashed the program with `OperationalError`. Now it is stored correctly. Playlists are saved as JSON, so loading a playlist can no longer run arbitrary code.
- **Correctness and robustness:** playlists no longer leak between calls because of the shared default list. `total_plays()` returns `0` instead of `None` for an empty catalog. `shuffle_pick()` returns `None` instead of raising `IndexError`. Real errors such as `KeyboardInterrupt` are no longer swallowed by a bare `except`.
- **Readability:** functions follow PEP 8 snake_case naming and have docstrings, variables have clear names (`loaded` instead of `l`), the magic number `100` is now `POPULARITY_THRESHOLD`, and long lines are wrapped. The code is easier to read and to explain.
- **Reusability:** the `if __name__ == "__main__":` guard means the module can be imported, for example by tests, without running the demo.
- **Behaviour kept:** the program still prints the same output (`multi-song playlist` / `popular niche <id> 290`), so the cleanup changed the quality of the code without breaking what it does.
