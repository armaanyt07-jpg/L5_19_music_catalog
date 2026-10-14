"""Music catalog and playlist manager for a music streaming service.

Stores songs and their play counts in an in-memory SQLite database,
rates song popularity, picks a random song and saves/loads playlists.
"""

import json
import random
import sqlite3

POPULARITY_THRESHOLD = 100

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE songs "
    "(id INTEGER PRIMARY KEY, title TEXT, artist TEXT, plays INTEGER)"
)


def add_song(title, artist, plays=0, playlist=None):
    """Insert a song into the catalog and append its title to a playlist.

    A new playlist is created when none is given. Returns the playlist.
    """
    if playlist is None:
        playlist = []
    conn.execute(
        "INSERT INTO songs (title, artist, plays) VALUES (?, ?, ?)",
        (title, artist, plays),
    )
    playlist.append(title)
    return playlist


def shuffle_pick():
    """Return the id of a random song, or None if the catalog is empty."""
    ids = [row[0] for row in conn.execute("SELECT id FROM songs")]
    if not ids:
        return None
    # Shuffle play is not a security feature, so a PRNG is fine here.
    return random.choice(ids)  # nosec B311


def popularity(title):
    """Rate a song as "popular", "niche" or "unknown" by its play count."""
    row = conn.execute(
        "SELECT plays FROM songs WHERE title = ?", (title,)
    ).fetchone()
    if row is None:
        return "unknown"
    return "popular" if row[0] > POPULARITY_THRESHOLD else "niche"


def save_playlist(playlist):
    """Serialise a playlist (list of titles) to a JSON string."""
    return json.dumps(playlist)


def load_playlist(blob):
    """Deserialise a playlist previously produced by save_playlist."""
    return json.loads(blob)


def total_plays():
    """Return the sum of play counts across all songs (0 if none)."""
    try:
        total = conn.execute("SELECT SUM(plays) FROM songs").fetchone()[0]
    except sqlite3.Error:
        return 0
    return total or 0


def main():
    """Run a short demonstration of the catalog."""
    playlist = add_song("Aurora", "Nila", 250)
    add_song("Monsoon", "Kavya", 40, playlist)
    blob = save_playlist(playlist)
    loaded = load_playlist(blob)
    if len(loaded) > 1:
        print("multi-song playlist")
    print(
        popularity("Aurora"),
        popularity("Monsoon"),
        shuffle_pick(),
        total_plays(),
    )


if __name__ == "__main__":
    main()
