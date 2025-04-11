#!/bin/bash

export FLASK_DEBUG=0
pip install -r requirements.txt

python app.py &

cd frontend/ && npm run dev
