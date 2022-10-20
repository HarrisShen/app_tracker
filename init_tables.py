import sqlite3

def init_db(db):
    with open('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

if __name__ == "__main__":
    con = sqlite3.connect("app_data.sqlite")
    init_db(con)