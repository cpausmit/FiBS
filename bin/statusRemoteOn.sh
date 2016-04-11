#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Startup daemon for dropbox copy on a given machine with specific log file.
#---------------------------------------------------------------------------------------------------
CLIENT="$1"
TASK="$2"

# setup FiBS
source /home/cmsprod/FiBS/setup.sh

isRunning=`ssh -x $CLIENT "ps auxw|grep fibsEngine.py|grep ${TASK}.cfg|grep -v grep|cut -d' ' -f1"`
if [ "$isRunning" != "" ]
then
  echo "RUNNING -- fibs engine (config:$TASK) is running on $CLIENT"
  exit 1
else
  echo "No engine (config:$TASK) runs on $CLIENT."
fi

exit 0
