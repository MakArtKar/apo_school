import sqlite3
import config


def get_table_size():
    with sqlite3.connect(config.DATABASE_NAME) as connection:
        cursor = connection.cursor()
        try:
            return cursor.execute("SELECT COUNT (*) FROM music").fetchone()[0]
        except:
            return 0


def fill_table(table_rows):
    with sqlite3.connect(config.DATABASE_NAME) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("CREATE TABLE music (file_id text, right_answer text, wrong_answers text)")
        except:
            cursor.execute("DELETE FROM music")

        cursor.executemany("INSERT INTO music VALUES (?,?,?)", table_rows)

        connection.commit()


def select_row(row_id):
    with sqlite3.connect(config.DATABASE_NAME) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        row = cursor.execute("SELECT * FROM music WHERE rowid = ?", (row_id,)).fetchone()
        return row


def select_all_rows():
    with sqlite3.connect(config.DATABASE_NAME) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        row = cursor.execute("SELECT * FROM music").fetchall()
        return row
