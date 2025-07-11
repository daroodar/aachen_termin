#!/bin/zsh
## First time setup on instance - follow the bellow "commented out" instructions - This doesn't do anything normally
: << 'EOF'
## Download and install Chrome
sudo wget -O /tmp/google-chrome-stable_current_x86_64.rpm https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum install -y /tmp/google-chrome-stable_current_x86_64.rpm
#
## Install additional dependencies that might be missing
sudo yum install -y xorg-x11-server-Xvfb gtk3 libXScrnSaver alsa-lib
EOF

# Start of script

ssh ec2-user@my-dev "mkdir -p /home/ec2-user/code/aachen-termin"
rsync -r --delete src .env execute.bash requirements.txt my-dev:/home/ec2-user/code/aachen-termin
/bin/zsh -x ./enable_crontab.sh
echo "Deployment done and crontab enabled at"
ssh ec2-user@my-dev "crontab -l"