from flask import Flask, render_template, request, g, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'test_app_data.sqlite'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def homepage():
    with app.app_context():
        db = get_db()
        db.row_factory = sqlite3.Row

        cur = db.cursor()
        cur.execute("SELECT * FROM job_info")
        rows = cur.fetchall()
        for i, row in enumerate(rows):
            update_id = row["last_status_update"]
            cur.execute("SELECT app_status, update_time, action_deadline FROM app_status_log WHERE update_id=(?)", (update_id,))
            status_info = cur.fetchone()
            keys, vals = row.keys() + status_info.keys(), list(row) + list(status_info)
            rows[i] = {k: v for k, v in zip(keys, vals)}
        rows = reversed(rows)
    return render_template("home.html", rows=rows)


@app.route("/add")
def add_record():
    return render_template("addnew.html")

@app.route("/api/update", methods=["POST"])
def update():
    request_data = request.get_json()
    print(request_data)

    insert_app_log = "INSERT INTO app_log VALUES (?,?,?,?,?)"
    update_job_entry = "UPDATE job_info SET app_status = (?) WHERE company = (?) AND position = (?)"

    company = request_data["company"]
    position = request_data["position"]
    status = request_data["status"]
    time = request_data["time"]
    note = ""

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(update_job_entry, (status, company, position))
            cur.execute(insert_app_log, (company, position, status, time, note))
            db.commit()
            msg = "Record successfully updated"
        except Exception as e:
            print(e)
            db.rollback()
            msg = "Update failed"
    return jsonify({"message": msg})

@app.route("/addrec", methods=["POST"])
def addrec():
    print(request.form)
    insert_app_log = "INSERT INTO app_log VALUES (?,?,?,?,?)"
    insert_job_entry = "INSERT INTO job_info VALUES (?,?,?,?,?,?,?,?,?,?)"
    update_job_entry = "UPDATE job_info SET app_status = (?) WHERE company = (?) AND position = (?)"
    select_job_entry = "SELECT * from job_info WHERE company = (?) AND position = (?)"

    company = request.form["company"]
    position = request.form["position"]
    status = request.form["status"]
    time = request.form["time"]
    note = request.form["note"]
    link = request.form["link"]
    posting_status = request.form["posting_status"]
    app_deadline = request.form["app_deadline"]
    company_type = request.form["company_type"]
    priority = request.form["priority"]
    app_portal = request.form["app_portal"]

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(
                select_job_entry,
                (company, position)
            )
            rows = cur.fetchall()
            if rows and status != None:
                cur.execute(
                    update_job_entry,
                    (status, company, position)
                )
            else:
                cur.execute(
                    insert_job_entry,
                    (company, position, link, posting_status, app_deadline, company_type, priority, app_portal, status, note)
                )                
            if status != "None":
                cur.execute(insert_app_log, (company, position, status, time, note))
            db.commit()
            msg = "Record successfully added"
        except Exception as e:
            print(e)
            db.rollback()
            msg = "error in insert operation"

    return render_template("result.html", msg=msg)


if __name__ == "__main__":
    app.run(debug=True)
