import sqlite3
import sys

def add_log(con, company, position, status, time, note=""):
    cur = con.cursor()
    insert_cmd = "INSERT INTO app_log VALUES (?,?,?,?,?)"
    try:
        cur.execute(insert_cmd, (company, position, status, time, note))
        con.commit()
    except sqlite3.IntegrityError:
        print("Repeat company & position, skipped")

if __name__ == "__main__":
    con = sqlite3.connect("app_data.sqlite")
    with open("job_update.log", "r") as input_file:
        for input_line in input_file.readlines():
            values = input_line.split(',')
            for i, v in enumerate(values):
                if not v.startswith('"') and not v.endswith('"'):
                    values[i] = '"' + v + '"'
            add_log(con, *values)
    con.close()
    