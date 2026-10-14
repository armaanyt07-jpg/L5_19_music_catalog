# Lab 5: Issues Found in `music_catalog.py`

Tools used: Pylint, Bandit, Flake8. The original reports are in `reports/before/`. The reports after the fixes are in the repo root (`pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt`).

| Result | Before | After |
|--------|--------|-------|
| Pylint score | 4.57/10 (19 messages) | **10.00/10** (0 messages) |
| Bandit | 4 issues (2 Medium, 2 Low) | **0 issues** |
| Flake8 | 7 issues | **0 issues** |

## Issue table (high and medium severity first)

Line numbers refer to the **original** file.

| # | Issue | Type | Line(s) | Description | Fix Approach | Status |
|---|-------|------|---------|-------------|--------------|--------|
| 1 | SQL injection (Bandit B608) | Security (Medium) | 10 | `addSong` builds the `INSERT` with `%` string formatting, so a title or artist containing `'` breaks the query and crafted input can change the SQL. I checked this: `addSong("Don't Stop", "X")` raised `sqlite3.OperationalError: near "t": syntax error`. | Use a parameterised query with `?` placeholders and pass the values as a tuple, so SQLite handles the quoting. | Fixed |
| 2 | Unsafe deserialisation with `pickle` (Bandit B301, B403) | Security (Medium) | 1, 29, 33 | `pickle.loads` can run arbitrary code if the blob comes from an untrusted source, such as a playlist file a user uploads. | A playlist is only a list of strings, so serialise it with `json.dumps` and `json.loads`. JSON cannot run code when it is loaded. | Fixed |
| 3 | Mutable default argument (Pylint W0102) | Bug (High) | 9 | `playlist=[]` is created once and shared by every call that leaves it out, so songs leak between "separate" playlists. I checked this: a later `addSong('A','B')` returned `['Aurora', 'Monsoon', 'A']`. | Default to `None` and create a new list inside the function. | Fixed |
| 4 | Bare `except:` (Pylint W0702, Flake8 E722) | Bug / Robustness (Medium) | 39 | It catches everything, including `KeyboardInterrupt`, `SystemExit` and programming errors, and hides them by returning 0. | Catch only `sqlite3.Error`. | Fixed |
| 5 | `totalPlays()` returns `None` on an empty catalog | Bug (Medium, found by hand) | 38 | `SUM()` over zero rows gives `NULL`, so the function returned `None`, not 0. None of the tools caught this. | Return `total or 0`. | Fixed |
| 6 | `shufflePick()` crashes on an empty catalog | Bug (Medium, found by hand) | 16–17 | `random.choice([])` raises `IndexError`. None of the tools caught this. | Return `None` when there are no songs. | Fixed |
| 7 | Code runs on import | Design (Medium, found by hand) | 52 | `main()` is called at module level, so `import music_catalog` runs the demo, which makes the module hard to test or reuse. | Wrap the call in `if __name__ == "__main__":`. | Fixed |
| 8 | Use of `random` (Bandit B311) | Security (Low) | 17 | Bandit warns that `random` is not cryptographically secure. | **False positive.** Shuffle play is not a security feature. I kept `random` and added `# nosec B311` with a comment explaining why. | Suppressed with justification |
| 9 | Function names not snake_case (Pylint C0103) | Style (Low) | 9, 15, 28, 32, 36 | `addSong`, `shufflePick`, `savePlaylist`, `loadPlaylist` and `totalPlays` break PEP 8 naming. | Renamed to `add_song`, `shuffle_pick`, `save_playlist`, `load_playlist` and `total_plays`. | Fixed |
| 10 | Missing docstrings (Pylint C0114, C0116) | Documentation (Low) | 1, 9, 15, 20, 28, 32, 36, 43 | There is no module docstring and no function docstrings. | Added a module docstring and a docstring for each function. | Fixed |
| 11 | Ambiguous variable name `l` (Flake8 E741) | Readability (Low) | 47 | `l` looks like `1` or `I` in many fonts. | Renamed `l` to `loaded`, and `pl` to `playlist`. | Fixed |
| 12 | Multiple statements on one line (Flake8 E701, Pylint C0321) | Style (Low) | 48 | `if len(l) > 1: print(...)` | Moved the body onto its own line. | Fixed |
| 13 | Lines too long (Flake8 E501, Pylint C0301) | Style (Low) | 6, 10, 21, 49 | Lines were longer than 79 characters (Flake8) or 100 (Pylint). | Wrapped them with implicit string concatenation and bracketed continuation lines. | Fixed |
| 14 | Unnecessary `else` after `return` (Pylint R1705) | Readability (Low) | 22–25 | The `else` adds nesting that does nothing. | Removed the `else` and de-indented its body. | Fixed |
| 15 | Old-style `%` formatting (Pylint C0209) | Style (Low) | 10 | Pylint suggests an f-string here. | Not applicable after fix #1: the query now uses placeholders, not string formatting. An f-string would have brought the SQL injection back. | Fixed by #1 |
| 16 | Magic number `100` | Readability (Low, found by hand) | 25 | The popularity threshold was hard-coded. | Moved it into a named constant, `POPULARITY_THRESHOLD`. | Fixed |

## Behaviour check

The program prints the same output before and after the fixes:

```
multi-song playlist
popular niche 1 290
```

(The third value comes from a random pick, so it can be `1` or `2`.)

Extra checks on the fixed version:
- `add_song("Don't Stop", "O'Brien", 5)` now stores the song correctly.
- An injection-style title (`x', 'y', 0); DROP TABLE songs; --`) is stored as a plain string, and the table is not affected.
- On an empty catalog, `shuffle_pick()` returns `None` and `total_plays()` returns `0`, with no crash.
- Two calls to `add_song` without a playlist argument now return two separate lists.
