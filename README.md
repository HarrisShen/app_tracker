# AppTracker: An Flask app for job application tracking

This Flask app provides a website where user can manage their job application history. The history entries of applications can be created, updated and deleted. The key information for a entry, like company name, position title and weblink of the posting are needed upon creation. Once the status of the job application changes, the entry can be updated on the webpage, reflecting the up-to-date status.

## Current version
0.5.0

## Build and Install

### Build from source
If you want to build from source Python file, make sure the wheel library is installed first:

`$ pip install wheel`

Running `setup.py` with Python gives you a command line tool to issue build-related commands. The `bdist_wheel` command will build a wheel distribution file.

`$ python setup.py bdist_wheel`

### Releases
Alternatively, the distribution files can be found in [releases](https://github.com/HarrisShen/app_tracker/releases)

### Installation
Copy the `.whl` file to the server machine and, preferably, set up a new virtualenv, then install the file with `pip`

`$ pip install trackerflask-*.*.*-py3-none-any.whl`

If it is the first time it runs on a machine, you need to run `init-db` to create the database in the Flask instance folder. The new database file can be found at `venv/var/flaskr-instance`.

## Deployment

### Configuration
The application is configured by a external `.py` file, in which the secret key and the file name for the database should be specified.

The full path of the file should be present in environment variables, under the name `TRACKAPP_SETTINGS`.

### Deploy to production
Flask is a WSGI application. A WSGI server is used to run the application, converting incoming HTTP requests to the standard WSGI environ, and converting outgoing WSGI responses to HTTP responses.

You may use WSGI server to host this app, like [Gunicorn](https://flask.palletsprojects.com/en/2.2.x/deploying/gunicorn/) and [Waitress](https://flask.palletsprojects.com/en/2.2.x/deploying/waitress/). On the other hand, a dedicated HTTP server may be safer, more efficient, or more capable. There is one catch though - you need to put the HTTP server in front of the WSGI server as a "reverse proxy", which involves some more configurations. For full guidance of how to set up the server, you may refer to the [Flask tutorial page](https://flask.palletsprojects.com/en/2.2.x/deploying/)
