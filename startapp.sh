#!/bin/bash

gunicorn --chdir src/ --worker-class eventlet app:app
