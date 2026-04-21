#!/bin/bash
source venv/bin/activate
lsof -ti:5001 | xargs kill -9 2>/dev/null
sleep 1
python app.py &
sleep 3
open index.html
trap "lsof -ti:5001 | xargs kill -9 2>/dev/null; exit" INT TERM EXIT
wait