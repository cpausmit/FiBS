#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Startup daemon for the dropbox copy on this machine
#---------------------------------------------------------------------------------------------------
TASK="$1"
if [ "$TASK" == "" ]
then
  echo ""; echo " Please specify task as parameter. EXIT!"; echo ""
  exit 1
fi

# make sure engine is not yet running

isEngineRunning=`ps auxw |grep fibsEngine.py | grep ${TASK}.cfg | cut -d' ' -f1`
if [ "$isEngineRunning" != "" ]
then
  echo 'ERROR -- fibs engine is already running. Do not start another one.'
  exit 1
else
  echo 'No engine runs on this machine yet.'
fi

# get a valid certificate
voms-proxy-init --valid 168:00 -voms cms

# setup the core programs
source /home/cmsprod/FiBS/setup.sh
source /home/cmsprod/PyCox/setup.sh

# start the engine
cd $FIBS_BASE
./fibsEngine.py --configFile=./config/${TASK}.cfg --task=${TASK}.py --list=${TASK}.list &
