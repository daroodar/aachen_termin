#!/bin/zsh
cd /home/ec2-user/code/aachen-termin
mkdir -p output
python3 -m venv .venv
export LOG_FILE_PATH=/home/ec2-user/code/aachen-termin/output/application.log
source .venv/bin/activate
pip install -qqr requirements.txt --upgrade
python3 src/main.py
deactivate