source /cvmfs/cms.cern.ch/cmsset_default.sh
cd     /home/cmsprod/cms/cmssw/044/CMSSW_*/src
eval  `scram runtime -sh`
source MitProd/Processing/bin/processing.sh
source /home/cmsprod/T2Tools/setup.sh
cd -
env
