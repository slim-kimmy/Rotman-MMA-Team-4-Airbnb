import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
# Define database path
DB_PATH = os.getenv("DB_PATH", "../data/users.db")

"""
Establish connection to the SQLite database.    
"""
def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

"""
Creates a user table if it does not exist based on the project requirements + additionals fields.
"""
def create_users_table():
    # Establish a connection to the database
    conn = get_db_connection()
    # Create cursor object
    cursor = conn.cursor()
    # SQL commands to check and create the users table
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
    # Commit and close the connection
    conn.commit()
    conn.close()

"""
Insert a new user into the database table.
"""
def insert_user(username, password, name, group_size, preferred_env, min_price, max_price):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create cursor object
    cursor = conn.cursor()
    # Safe SQL command to inser a new user
    cursor.execute('''
        INSERT INTO users (username, password, name, group_size, preferred_env, min_price, max_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, password, name, group_size, preferred_env, min_price, max_price))
    # Commit and close the connection
    conn.commit()
    conn.close()

"""
Edits the user in the database given a username (unique identifier).
"""
def edit_user(username, name, group_size, preferred_env, min_price, max_price):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create cursor object
    cursor = conn.cursor()
    # Updates users filtered based on username
    cursor.execute('''
        UPDATE users
        SET name = ?, group_size = ?, preferred_env = ?, min_price = ?, max_price = ?
        WHERE username = ?
    ''', (name, group_size, preferred_env, min_price, max_price, username))
    conn.commit()
    conn.close()

"""
Returns an SQL representation of the users information filtered based on the username
"""
def view_user(username):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create cursor object
    cursor = conn.cursor()
    # Execute query to retrieve user information
    cursor.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,))
    # Fetch one user
    user = cursor.fetchone()
    # Close the connection and return user
    conn.close()
    return user

"""
Removes a user from the table based on the username.
"""
def delete_user(username):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create cursor object
    cursor = conn.cursor()
    # Execute delete command
    cursor.execute('''
        DELETE FROM users WHERE username = ?
    ''', (username,))
    # Commit and close the connection
    conn.commit()
    conn.close()

# Create the users table if it does not exist
create_users_table()