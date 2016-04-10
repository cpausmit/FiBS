#!/bin/bash

TASK="$1"
machines=`ls $FIBS_LOGS/$TASK |grep err |sed 's@^.*root-@@'| sed 's@\.err@@'|sort -u`

for machine in $machines
do

  cmd="stopRemoteOn.sh $machine $TASK"
  echo Exec: $cmd
  $cmd

done