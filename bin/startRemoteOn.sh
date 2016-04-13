#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Startup daemon for the dropbox copy on a given machine with specific log file
#---------------------------------------------------------------------------------------------------
CLIENT="$1"
TASK="$2"
if [ "$CLIENT" == "" ] || [ "$TASK" == "" ]
then
  echo ""; echo " Please specify client and task as parameter. EXIT!"; echo ""
  exit 1
fi

# setup FiBS
source /home/cmsprod/FiBS/setup.sh

# test whether there is already something running
isRunning=`ssh -x $CLIENT "ps auxw|grep fibsEngine.py|grep ${TASK}.cfg|grep -v grep|cut -d' ' -f1"`
if [ "$isRunning" != "" ]
then
  echo " is already RUNNING -- fibs engine (config:$TASK on $CLIENT)"
  exit 1
fi 

# start up the engine on the remote machine
echo " STARTING the FiBS engine with task $TASK on $CLIENT"
ssh -x $CLIENT "nohup ./FiBS/bin/start.sh $TASK > $FIBS_LOGS/${TASK}_${CLIENT}.log 2>&1 &"

exit $?
