cd src
clear
gunicorn --bind=0.0.0.0 --worker-class eventlet -w 1 webapp.api:app

