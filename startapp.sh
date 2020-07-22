cd src
clear
gunicorn --worker-class eventlet -w 1 webapp.api:app

