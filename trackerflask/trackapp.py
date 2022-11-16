import json
import time
from flask import (
    Blueprint, session, current_app, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from trackerflask.auth import login_required
from trackerflask.db import get_db

bp = Blueprint('trackapp', __name__)


@bp.route('/')
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM job_info LEFT JOIN app_status_log "
        "ON job_info.last_status_update = app_status_log.update_id "
        "WHERE user_id=(?)", (user_id,))
    rows = cur.fetchall()
    rows = reversed(rows)
    return render_template('trackapp/index.html', rows=rows, user_id=user_id)

def get_form_values(form_dict, keys):
    return tuple(form_dict.get(k) for k in keys)

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        user_id = session.get('user_id')

        print(request.form)
        insert_app_log = (
            "INSERT INTO app_status_log "
            "(pos_id, app_status, update_time, action_deadline) "
            "VALUES (?,?,?,?)"
        )
        insert_job_entry = (
            "INSERT INTO job_info (user_id, company, position, pos_link, "
            "posting_status, deadline, company_type, app_priority, app_portal, "
            "note) VALUES (?,?,?,?,?,?,?,?,?,?)"
        )

        form_info = request.form.to_dict()
        form_info["user_id"] = user_id

        with current_app.app_context():
            db = get_db()
            cur = db.cursor()
            try:
                param_keys = (
                    "user_id", "company", "position", "link", 
                    "posting_status", "app_deadline", "company_type", 
                    "priority", "app_portal", "note"
                )
                cur.execute(insert_job_entry, get_form_values(form_info, param_keys))
                if form_info["status"] != "None":
                    param_keys = ("user_id", "company", "position")
                    cur.execute(
                        "SELECT pos_id FROM job_info WHERE user_id=(?) AND company=(?) AND position=(?)",
                        get_form_values(form_info, param_keys)
                    )
                    form_info["pos_id"] = cur.fetchone()["pos_id"]
                    param_keys = ("pos_id", "status", "time", "app_deadline")
                    cur.execute(insert_app_log, get_form_values(form_info, param_keys))
                    cur.execute(
                        "SELECT update_id FROM app_status_log WHERE pos_id=(?) AND update_time=(?)",
                        get_form_values(form_info, ("pos_id", "time"))
                    )
                    form_info["update_id"] = cur.fetchone()["update_id"]
                    cur.execute(
                        "UPDATE job_info SET last_status_update=(?) WHERE pos_id=(?)",
                        get_form_values(form_info, ("update_id", "pos_id"))
                    )
                cur.execute(
                    "INSERT INTO change_log (change_type, pos_id, content, time_stamp) VALUES (?,?,?,?)", 
                    ("CREATE", form_info["pos_id"], json.dumps(form_info), time.time())
                )
                db.commit()
                msg = "Record successfully created"
            except Exception as e:
                print(e)
                db.rollback()
                msg = "Failed to create record"
        return render_template("trackapp/result.html", msg=msg)

    return render_template("trackapp/create.html")

def get_pos_info(pid, check_user=True):
    pos_info = get_db().execute(
        "SELECT * FROM job_info LEFT JOIN app_status_log "
        "ON job_info.last_status_update = app_status_log.update_id "
        "WHERE job_info.pos_id=(?)",
        (pid,)
    ).fetchone()

    if pos_info is None:
        abort(404, f"Position {pid} doesn't exist.")

    if check_user and pos_info['user_id'] != g.user['id']:
        abort(403)

    return pos_info

@bp.route("/<int:pid>/update", methods=["GET", "POST"])
@login_required
def update(pid):
    pos_info = get_pos_info(pid)
    if request.method == 'POST':
        user_id = session.get('user_id')
        print(request.form)
        insert_app_log = (
            "INSERT INTO app_status_log (pos_id, app_status, update_time, "
            "action_deadline) VALUES (?,?,?,?)"
        )
        update_job_entry = (
            "UPDATE job_info SET pos_link = ?, posting_status = ?, deadline = ?, "
            "company_type = ?, app_priority = ?, app_portal = ?, note =? WHERE pos_id = ?"
        )

        form_info = request.form.to_dict()
        form_info["user_id"] = user_id
        form_info["pos_id"] = pid

        with current_app.app_context():
            db = get_db()
            cur = db.cursor()
            try:
                param_keys = (
                    "link", "posting_status", "app_deadline", "company_type", 
                    "priority", "app_portal", "note", "pos_id"
                )
                cur.execute(update_job_entry, get_form_values(form_info, param_keys))
                if form_info["status"] != "None":
                    param_keys = ("pos_id", "status", "time", "action_deadline")
                    cur.execute(insert_app_log, get_form_values(form_info, param_keys))
                    cur.execute(
                        "SELECT update_id FROM app_status_log WHERE pos_id=(?) AND update_time=(?)",
                        get_form_values(form_info, ("pos_id", "time"))
                    )
                    form_info["update_id"] = cur.fetchone()["update_id"]
                    cur.execute(
                        "UPDATE job_info SET last_status_update=(?) WHERE pos_id=(?)",
                        get_form_values(form_info, ("update_id", "pos_id"))
                    )
                cur.execute(
                    "INSERT INTO change_log (change_type, pos_id, content, time_stamp) VALUES (?,?,?,?)", 
                    ("UPDATE", form_info["pos_id"], json.dumps(form_info), time.time())
                )
                db.commit()
                msg = "Record successfully updated"
            except Exception as e:
                print(e)
                db.rollback()
                msg = "Failed to update record"
        return render_template('trackapp/result.html', msg=msg)

    return render_template('trackapp/update.html', pos_info=pos_info)

@bp.route('/<int:pid>/delete', methods=('POST',))
@login_required
def delete(pid):
    get_pos_info(pid)
    with current_app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute('DELETE FROM job_info WHERE pos_id = ?', (pid,))
        cur.execute('DELETE FROM app_status_log WHERE pos_id = ?', (pid,))
        cur.execute('DELETE FROM change_log WHERE pos_id = ?', (pid,))
        db.commit()
    return redirect(url_for('trackapp.index'))