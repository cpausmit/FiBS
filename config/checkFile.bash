source /cvmfs/cms.cern.ch/cmsset_default.sh
cd     /home/cmsprod/cms/cmssw/046/CMSSW_*/src
eval  `scram runtime -sh`
source MitProd/Processing/bin/processing.sh
# make sure we have a certificate
voms-proxy-init --valid 168:00 -voms cms
source /home/cmsprod/Tools/T2Tools/setup.sh
cd -
env
