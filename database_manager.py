import sqlite3
import pandas as pd

DB_NAME = "trading_system.db"

def init_db():
    """ Initialize User Authentication Tables """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            is_approved INTEGER DEFAULT 0
        )
    ''')
    
    # Automatically seed the Master Admin account
    c.execute("INSERT OR IGNORE INTO users (username, password, is_approved) VALUES (?, ?, ?)", 
              ('traderpratik', 'traderpratik', 1))
    
    conn.commit()
    conn.close()

def register_user(username, password):
    """ Register a new user, defaults to NOT approved """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, is_approved) VALUES (?, ?, ?)", (username, password, 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists
    finally:
        conn.close()

def authenticate_user(username, password):
    """ Checks login credentials and approval status """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT is_approved FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {"success": True, "is_approved": bool(user[0])}
    return {"success": False}

def get_all_users():
    """ Returns a dataframe of all users for the Admin panel """
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT username, is_approved FROM users WHERE username != 'traderpratik'", conn)
    conn.close()
    return df

def approve_user(username):
    """ Administrator logic to approve an account """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_approved=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()
