![Design of auto jenkins jobs](design.jpg)

## gitlab system hook
- Repository Upadate events
- will use gitlab file raw dowload to check availibilitayy of Jenkins file

    https://gitlab.maduma.org/maduma/pompiste/-/raw/master/Jenkinsfile
    https://raw.githubusercontent.com/maduma/flutiste/master/Jenkinsfile

## make usre flask is running single threaded
- FLASK_APP=web.py flask run --without-threads
- gunicorn --reload --workers 1 --threads 1 --bind 0.0.0.0:5000 web:app
gunicorn --reload --workers 1 --threads 1 --bind 0.0.0.0:5000 web:app
