import sqlite3

DATABASE = "bot.db"


def connect():
    return sqlite3.connect(DATABASE)


def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            voice TEXT NOT NULL DEFAULT 'omr'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            voice TEXT NOT NULL,
            file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO users (user_id, voice)
        VALUES (?, 'omr')
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()


def get_voice(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT voice FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return "omr"


def set_voice(user_id, voice):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (user_id, voice)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET voice = excluded.voice
        """,
        (user_id, voice)
    )

    conn.commit()
    conn.close()


def save_to_library(user_id, text, voice, file_path):
    """Save audio to user's library."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO library (user_id, text, voice, file_path)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, text, voice, file_path)
    )

    conn.commit()
    library_id = cursor.lastrowid
    conn.close()

    return library_id


def get_library(user_id, limit=10):
    """Get user's library (most recent first)."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, text, voice, file_path, created_at
        FROM library
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit)
    )

    results = cursor.fetchall()
    conn.close()

    return results


def get_library_item(user_id, item_id):
    """Get a specific library item."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, text, voice, file_path, created_at
        FROM library
        WHERE user_id = ? AND id = ?
        """,
        (user_id, item_id)
    )

    result = cursor.fetchone()
    conn.close()

    return result


def delete_from_library(user_id, item_id):
    """Delete audio from user's library."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM library
        WHERE user_id = ? AND id = ?
        """,
        (user_id, item_id)
    )

    conn.commit()
    conn.close()