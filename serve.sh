#!/bin/bash

cd `dirname $0`

source venv/bin/activate

#python python/application.py
gunicorn --pythonpath python application:app
