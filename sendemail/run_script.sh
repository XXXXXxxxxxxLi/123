#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 {weekly|monthly}"
    exit 1
fi

source /home/user1/PycharmProjects/pythonProject/venv/bin/activate
python3 /home/user1/PycharmProjects/pythonProject/sent_email2user/changfa_test.py $1
deactivate


