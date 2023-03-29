from collections import Counter
import json
import math
import time
import os

from bs4 import BeautifulSoup
import requests
from flask import (
    Blueprint, session, current_app, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from trackerflask.auth import login_required
from trackerflask.db import get_db
from trackerflask.gpt import GPT

bp = Blueprint('trackapp', __name__)
gptAPI = GPT(os.environ.get('APIKEY'))

def get_page_index(page_num, each_page=20):
    start = (page_num - 1) * each_page
    end = page_num * each_page
    return start, end

@bp.route('/')
def index():
    query = request.args.get("query", type=str)
    page_num = request.args.get("page", default=1, type=int)
    each_page = 20
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    cur = db.cursor()
    if query is None:
        cur.execute(
            "SELECT * FROM job_info LEFT JOIN app_status_log "
            "ON job_info.last_status_update = app_status_log.update_id "
            " WHERE user_id = ? ORDER BY update_time", (user_id,))
    else:
        cur.execute(
            "SELECT * FROM job_info LEFT JOIN app_status_log "
            "ON job_info.last_status_update = app_status_log.update_id "
            "WHERE (user_id = ?) AND (company LIKE ?) ORDER BY update_time",
            (user_id, f"%{query}%"))
    rows = cur.fetchall()
    rows = list(reversed(rows))
    n_rows = len(rows)
    status_stats = Counter([row["app_status"] for row in rows])
    status_stats = (
        f'Ready - {status_stats["Ready"]}, Ongoing - {status_stats["Ongoing"]}, '
        f'Submitted - {status_stats["Submitted"]}, Interview - {status_stats["Interview"]} '
        f'Rejected - {status_stats["Rejected"]}, Offer - {status_stats["Offer"]}'
    )
    maxpage = math.ceil(n_rows / each_page)
    start, end = get_page_index(page_num, each_page=each_page)
    rows = rows[start: end]
    query_info = "" if query is None else f'Search for "{query}", '
    page_info = f"{query_info}{min(start + 1, n_rows)}-{min(end, n_rows)} in {n_rows} entries"
    return render_template(
        'trackapp/index.html', rows=rows, user_id=user_id, currpage=page_num, maxpage=maxpage, 
        pageinfo=page_info, status_stats=status_stats)

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
                param_keys = ("user_id", "company", "position")
                cur.execute(
                    "SELECT pos_id FROM job_info WHERE user_id=(?) AND company=(?) AND position=(?)",
                    get_form_values(form_info, param_keys)
                )
                form_info["pos_id"] = cur.fetchone()["pos_id"]
                if form_info["status"] != "None":
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

@bp.route('/search', methods=('POST',))
@login_required
def search():
    query_text = request.get_json()["text"]
    print(request.get_json())
    with current_app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT company FROM job_info WHERE company LIKE ?', (f"{query_text}%",))
        res = cur.fetchall()
    return jsonify([s[0] for s in res])

def get_app_history(pid):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM app_status_log WHERE pos_id=(?)", (pid,))
    app_history = cur.fetchall()
    return app_history

@bp.route("/<int:pid>/details")
@login_required
def details(pid):
    pos_info = get_pos_info(pid)
    app_history = get_app_history(pid)
    return render_template('trackapp/details.html', pos_info=pos_info, history=app_history)

@bp.route("/gpt-parse", methods=["POST"])
def gpt_parse():
    url = request.get_json()["url"]
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.body
    # text = soup.select('script[type="application/ld+json"]')[0].text.strip()
    prompt = f'''
        This is a job posting from "{url}", please parse the following information: company name, 
        job(position/program) title, job description, job requirements, job location, job type, 
        shool year requirement, visa/sponsorship requirement, application deadline. Response in JSON format.
        Here is the body string of the job web page:
        {text}'''
    response = gptAPI.getResponse(prompt=prompt)
    return jsonify(json.load(response))
