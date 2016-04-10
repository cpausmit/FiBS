#!/bin/bash

# define the task
TASK="$1"
if [ "$TASK" == "" ]
then
  echo ""; echo " Please specify task as parameter. EXIT!"; echo ""
  exit 1
fi

# setup our queue system
source ~/FiBS/setup.sh

# get out list in the consume space
cd $FIBS_BASE
cp ./config/$TASK.list $FIBS_WORK/

workers="t3serv012.mit.edu t3serv015.mit.edu"
workers="$workers t3btch096.mit.edu t3btch097mit.edu t3btch098.mit.edu t3btch099.mit.edu"
workers="$workers t3btch101.mit.edu t3btch102mit.edu t3btch103.mit.edu t3btch104.mit.edu"
workers="$workers t3btch105.mit.edu"

# start the various workers
for worker in $workers
do
  echo Starting task $TASK on batch worker: $worker
  startRemoteOn.sh $worker $TASK
done

exit 0