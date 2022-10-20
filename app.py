from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)

DATABASE = 'app_data.sqlite'


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
        cur.execute("select * from job_info")

        rows = cur.fetchall()
    return render_template("home.html", rows=rows)


@app.route("/update")
def update_record():
    return render_template("update.html")


@app.route("/addrec", methods=["POST"])
def addrec():
    print(request.form)
    insert_app_log = "INSERT INTO app_log VALUES (?,?,?,?,?)"
    insert_job_entry = "INSERT INTO job_info VALUES (?,?,?,?,?,?,?,?,?,?)"
    update_job_entry = "UPDATE job_info SET app_status = (?) WHERE company = (?) AND position = (?)"
    select_job_entry = "SELECT job_info WHERE company = (?) AND position = (?)"

    company = request.form["company"]
    position = request.form["position"]
    status = request.form["status"]
    time = request.form["time"]
    note = request.form["note"]
    if "new_entry" in request.form:
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
            if status != "None":
                cur.execute(insert_app_log, (company, position, status, time, note))
            if "new_entry" in request.form:
                cur.execute(
                    insert_job_entry,
                    (company, position, link, posting_status, app_deadline, company_type, priority, app_portal, status,
                     note)
                )
            else:
                cur.execute(
                    update_job_entry,
                    (status, company, position)
                )
            db.commit()
            msg = "Record successfully added"
        except Exception as e:
            print(e)
            db.rollback()
            msg = "error in insert operation"

    return render_template("result.html", msg=msg)


if __name__ == "__main__":
    app.run(debug=True)
