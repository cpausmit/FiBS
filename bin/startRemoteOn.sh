#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Startup daemon for the dropbox copy on a given machine with specific log file
#---------------------------------------------------------------------------------------------------
CLIENT="$1"
TASK="$2"

# setup FiBS
source /home/cmsprod/FiBS/setup.sh

# set off the engine on the remote machine
ssh -x $CLIENT "nohup ./FiBS/bin/start.sh $TASK > $FIBS_LOGS/${TASK}_${CLIENT}.log 2>&1 &"
