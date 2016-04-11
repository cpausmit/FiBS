#!/bin/bash
#---------------------------------------------------------------------------------------------------
# FiBS services.
#
#---------------------------------------------------------------------------------------------------
# define the task
SERVICE="$1"
TASK="$2"
if [ "$TASK" == "" ]
then
  echo ""; echo " Please specify task as parameter. EXIT!"; echo ""
  exit 1
fi

case "$SERVICE" in
  start)
    script=startRemoteOn.sh;;
  stop)
    script=stopRemoteOn.sh;;
  status)
    script=statusRemoteOn.sh;;
  *)
    echo $"Usage: $0 {start|stop|restart|condrestart|status}"
    exit 1
esac


# setup our queue system
source ~/FiBS/setup.sh

# get our list into the consume space
if [ "$SERVICE" == "cleanstart" ] 
then
  cd $FIBS_BASE
  cp ./list/$TASK.list $FIBS_WORK/
fi

# get list of batch workers
workers=`cat ./config/workers.cfg`

# start the various workers
for worker in $workers
do
  $script $worker $TASK
done

exit 0