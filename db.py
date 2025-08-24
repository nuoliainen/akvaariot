import sqlite3
from flask import g

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    con = get_connection()
    try:
        result = con.execute(sql, params)
        con.commit()
        g.last_insert_id = result.lastrowid
    except sqlite3.Error:
        con.rollback()
        raise
    finally:
        con.close()

def last_insert_id():
    return g.last_insert_id    
    
def execute_multiple(commands_with_params):
    """Executes multiple different SQL commands in a single transaction."""
    con = get_connection()
    try:
        for sql, params in commands_with_params:
            con.execute(sql, params)
        con.commit()
    except sqlite3.Error:
        con.rollback()
        raise
    finally:
        con.close()

def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
