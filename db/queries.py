import sqlite3

DB_NAME = "bot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    # Notes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        title TEXT,
        file_id TEXT
    )
    """)

    # Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY
    )
    """)

    # Reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        status TEXT DEFAULT 'open'
    )
    """)

    conn.commit()
    conn.close()


# ---------- USERS ----------
def add_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    except:
        pass

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    data = cursor.fetchall()

    conn.close()
    return [d[0] for d in data]


# ---------- CATEGORY ----------
def add_category(name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    except:
        pass

    conn.commit()
    conn.close()


def get_categories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM categories")
    data = cursor.fetchall()

    conn.close()
    return [d[0] for d in data]


# ---------- NOTES ----------
def add_note(category, title, file_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO notes (category, title, file_id) VALUES (?, ?, ?)",
        (category, title, file_id)
    )

    conn.commit()
    conn.close()


def get_notes_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title FROM notes WHERE category=?",
        (category,)
    )

    data = cursor.fetchall()
    conn.close()
    return data
    

def get_note_by_id(note_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT title, file_id FROM notes WHERE id=?",
        (note_id,)
    )

    data = cursor.fetchone()
    conn.close()
    return data


def delete_note(note_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))

    conn.commit()
    conn.close()


def update_note(note_id, title, file_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE notes SET title=?, file_id=? WHERE id=?",
        (title, file_id, note_id)
    )

    conn.commit()
    conn.close()


# ---------- REPORTS ----------
def add_report(user_id, message):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reports (user_id, message) VALUES (?, ?)",
        (user_id, message)
    )

    report_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return report_id


def get_report(report_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, message FROM reports WHERE id=?",
        (report_id,)
    )

    data = cursor.fetchone()
    conn.close()
    return data


def close_report(report_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE reports SET status='closed' WHERE id=?",
        (report_id,)
    )

    conn.commit()
    conn.close()