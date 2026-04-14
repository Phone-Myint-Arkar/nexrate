#!/bin/bash
source venv/bin/activate
lsof -ti:5001 | xargs kill -9
sleep 1
python app.py &
sleep 2
open index.html
wait