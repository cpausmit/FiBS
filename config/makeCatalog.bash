source /cvmfs/cms.cern.ch/cmsset_default.sh
cd     /home/cmsprod/cms/cmssw/044/CMSSW_*/src
eval  `scram runtime -sh`
source MitProd/Processing/bin/processing.sh
source /home/cmsprod/Tools/T2Tools/setup.sh
cd -
env

# make sure we have a certificate
timeleft=`voms-proxy-info -timeleft`
if (( $timeleft < 100000 ))
then
  if ! [ -z $DEBUG ]
  then
    echo " DEBUG - Re-initialize proxy."
  fi
  voms-proxy-init --valid 168:00 -voms cms
else
  if ! [ -z $DEBUG ]
  then
    echo " DEBUG - Proxy is still valid for $timeleft second."
  fi
fi
