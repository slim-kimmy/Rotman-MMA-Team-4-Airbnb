import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "./data/users.db")

def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

def create_users_table():
    """Create the table for users if it does not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            group_size INTEGER NOT NULL,
            preferred_env TEXT NOT NULL,
            min_price REAL NOT NULL,
            max_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(username, password, name, group_size, preferred_env, min_price, max_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password, name, group_size, preferred_env, min_price, max_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, password, name, group_size, preferred_env, min_price, max_price))
    conn.commit()
    conn.close()

def edit_user(username, name, group_size, preferred_env, min_price, max_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET name = ?, group_size = ?, preferred_env = ?, min_price = ?, max_price = ?
        WHERE username = ?
    ''', (name, group_size, preferred_env, min_price, max_price, username))
    conn.commit()
    conn.close()

def view_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()
    conn.close()
    # Have to cast this to a dict 
    return user
