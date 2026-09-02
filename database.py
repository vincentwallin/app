import sqlite3
import hashlib
import os
from datetime import datetime

DB_NAME = "social_app.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT,
            image BLOB,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            UNIQUE(post_id, user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            code TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            UNIQUE(group_id, user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_user(username, password):
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (username, password, created_at)
            VALUES (?, ?, ?)
            """,
            (
                username,
                hash_password(password),
                datetime.now().isoformat()
            )
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE username = ? AND password = ?
        """,
        (username, hash_password(password))
    ).fetchone()

    conn.close()

    return user


def create_post(user_id, text, image):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO posts
        (user_id, text, image, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            text,
            image,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_posts():
    conn = get_connection()

    posts = conn.execute("""
        SELECT
            posts.*,
            users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.id DESC
    """).fetchall()

    conn.close()

    return posts


def toggle_like(post_id, user_id):
    conn = get_connection()

    existing = conn.execute(
        """
        SELECT id FROM likes
        WHERE post_id = ? AND user_id = ?
        """,
        (post_id, user_id)
    ).fetchone()

    if existing:
        conn.execute(
            "DELETE FROM likes WHERE id = ?",
            (existing["id"],)
        )
    else:
        conn.execute(
            """
            INSERT INTO likes (post_id, user_id)
            VALUES (?, ?)
            """,
            (post_id, user_id)
        )

    conn.commit()
    conn.close()


def get_like_count(post_id):
    conn = get_connection()

    result = conn.execute(
        "SELECT COUNT(*) AS count FROM likes WHERE post_id = ?",
        (post_id,)
    ).fetchone()

    conn.close()

    return result["count"]


def user_liked(post_id, user_id):
    conn = get_connection()

    result = conn.execute(
        """
        SELECT id FROM likes
        WHERE post_id = ? AND user_id = ?
        """,
        (post_id, user_id)
    ).fetchone()

    conn.close()

    return result is not None


def add_comment(post_id, user_id, text):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO comments
        (post_id, user_id, text, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            post_id,
            user_id,
            text,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_comments(post_id):
    conn = get_connection()

    comments = conn.execute("""
        SELECT
            comments.*,
            users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE post_id = ?
        ORDER BY comments.id ASC
    """, (post_id,)).fetchall()

    conn.close()

    return comments


def create_group(name, description, code, owner_id):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO groups
        (name, description, code, owner_id, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            description,
            code,
            owner_id,
            datetime.now().isoformat()
        )
    )

    group_id = cursor.lastrowid

    conn.execute(
        """
        INSERT INTO group_members
        (group_id, user_id)
        VALUES (?, ?)
        """,
        (group_id, owner_id)
    )

    conn.commit()
    conn.close()

    return group_id


def get_groups():
    conn = get_connection()

    groups = conn.execute("""
        SELECT groups.*, users.username AS owner
        FROM groups
        JOIN users ON groups.owner_id = users.id
        ORDER BY groups.id DESC
    """).fetchall()

    conn.close()

    return groups


def join_group(group_id, user_id, code):
    conn = get_connection()

    group = conn.execute(
        "SELECT * FROM groups WHERE id = ?",
        (group_id,)
    ).fetchone()

    if not group:
        conn.close()
        return False, "Gruppen finns inte."

    if group["code"] != code:
        conn.close()
        return False, "Fel gruppkod."

    try:
        conn.execute(
            """
            INSERT INTO group_members
            (group_id, user_id)
            VALUES (?, ?)
            """,
            (group_id, user_id)
        )

        conn.commit()
        conn.close()

        return True, "Du gick med i gruppen!"

    except sqlite3.IntegrityError:
        conn.close()
        return False, "Du är redan medlem."


def get_user_groups(user_id):
    conn = get_connection()

    groups = conn.execute("""
        SELECT groups.*
        FROM groups
        JOIN group_members
        ON groups.id = group_members.group_id
        WHERE group_members.user_id = ?
        ORDER BY groups.id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return groups


def add_message(group_id, user_id, text):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO messages
        (group_id, user_id, text, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            group_id,
            user_id,
            text,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_messages(group_id):
    conn = get_connection()

    messages = conn.execute("""
        SELECT
            messages.*,
            users.username
        FROM messages
        JOIN users ON messages.user_id = users.id
        WHERE group_id = ?
        ORDER BY messages.id ASC
    """, (group_id,)).fetchall()

    conn.close()

    return messages
