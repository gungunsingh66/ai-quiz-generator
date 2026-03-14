import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    # results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        topic TEXT,
        difficulty TEXT,
        score INTEGER,
        total INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

def create_user(username, password):

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    # hash the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def verify_user(username, password):

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        stored_password = result[0]

        if bcrypt.checkpw(password.encode(), stored_password):
            return True

    return False

def get_results(username):

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT topic, difficulty, score, total, date FROM results WHERE username=? ORDER BY date DESC",
        (username,)
    )

    data = cursor.fetchall()

    conn.close()

    return data

def save_result(username, topic, difficulty, score, total):

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO results (username, topic, difficulty, score, total) VALUES (?, ?, ?, ?, ?)",
        (username, topic, difficulty, score, total)
    )

    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, topic, score, total
    FROM results
    ORDER BY score DESC
    LIMIT 10
    """)

    data = cursor.fetchall()
    conn.close()
    return data