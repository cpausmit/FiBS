#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Stop daemon for the dropbox copy on a given machine with specific log file
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

# set off the engine on the remote machine
pid=`ssh -x $CLIENT \
     "ps auxw | grep fibsEngine.py | grep $TASK | grep -v grep | tr -s ' ' | cut -d ' ' -f2"`

if [ "$pid" == "" ]
then
  echo " No more activity on $CLIENT. EXIT!"
  exit 0
fi

echo " Kill Pid $pid on $CLIENT"
ssh -x $CLIENT "kill $pid"

exit 0
