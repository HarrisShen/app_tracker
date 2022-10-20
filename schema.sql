CREATE TABLE job_info(
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    weblink TEXT,
    posting_status TEXT,
    deadline TEXT,
    company_type TEXT,
    app_priority INTEGER,
    app_portal TEXT,
    app_status TEXT,
    note TEXT,
    PRIMARY KEY(company, position)
);
CREATE TABLE app_log(
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    app_status TEXT NOT NULL,
    update_time TEXT NOT NULL,
    note TEXT,
    PRIMARY KEY(company, position, app_status, update_time)
);