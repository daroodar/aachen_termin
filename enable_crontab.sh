#!/bin/zsh
ssh ec2-user@my-dev "crontab -" << 'EOF'
# NOTE: Time is in GMT
# Every 5 minutes from 5:00 AM to 6:59 AM
*/5 5-6 * * * /home/ec2-user/code/aachen-termin/execute.bash

# Every 15 minutes for the rest of the day (0-4 AM and 7-23 PM)
*/15 0-4,7-23 * * * /home/ec2-user/code/aachen-termin/execute.bash
EOF