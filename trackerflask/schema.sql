DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS job_info;
DROP TABLE IF EXISTS app_status_log;
DROP TABLE IF EXISTS change_log;

CREATE TABLE user(
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE job_info(
    pos_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    pos_link TEXT,
    posting_status TEXT,
    deadline TEXT,
    company_type TEXT,
    app_priority INTEGER,
    app_portal TEXT,
    last_status_update INTEGER,
    note TEXT,
    UNIQUE(user_id, company, position),
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(last_status_update) REFERENCES app_log(update_id)
);

CREATE TABLE app_status_log(
    update_id INTEGER PRIMARY KEY,
    pos_id INTEGER NOT NULL,
    app_status TEXT NOT NULL,
    update_time TEXT NOT NULL,
    action_deadline TEXT,
    FOREIGN KEY(pos_id) REFERENCES job_info(pos_id)
);

CREATE TABLE change_log(
    change_id INTEGER PRIMARY KEY,
    change_type TEXT NOT NULL,
    pos_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    time_stamp REAL NOT NULL,
    FOREIGN KEY(pos_id) REFERENCES job_info(pos_id)
);