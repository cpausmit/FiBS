# make sure we have a certificate
voms-proxy-init --valid 168:00 -voms cms >& /dev/null
source $HOME/Panda/Kraken/setup.sh
source /home/cmsprod/Tools/Dools/setup.sh
source /home/cmsprod/Tools/T2Tools/setup.sh
cd -
env
