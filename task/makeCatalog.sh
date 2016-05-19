#!/bin/bash

# initialize
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd     /home/cmsprod/cms/cmssw/044/CMSSW_*/src
eval  `scram runtime -sh`
source MitProd/Processing/bin/processing.sh
source /home/cmsprod/T2Tools/setup.sh
cd -

# now go
bookdset="$1"
book=`echo $bookdset | cut -d':' -f1`
dset=`echo $bookdset | cut -d':' -f2`
mitcfg=`echo $book | cut -d' ' -f1`
version=`echo $book | cut -d' ' -f2`
if [ "$book" == "" ] || [ "$dset" == "" ]
then
  echo " Please specify book: ex. filefi/044  and dset: ex. SingleMu+PromptReco+AOD"
  exit 1
fi

cata=/home/cmsprod/catalog/t2mit/$book
hadoop=/cms/store/user/paus/$book
files=`t2tools.py --action ls --source $hadoop/$dset/crab_0* | cut -d' ' -f2`

nFiles=`echo $files | wc -w`
i=0

rm -f RawFiles.00.$$
touch RawFiles.00.$$
for file in $files
do
   i=$(($i + 1))
   echo "   -- next file: $file ($i of $nFiles)"  
   oldFile=`echo $file | sed 's@root://xrootd.cmsaf.mit.edu/@/cms@'`
   entry=`catalogFile.sh /mnt/hadoop$file | grep 'XX-CATALOG-XX 0000' | sed 's@XX-CATALOG-XX 0000 @@'`

   if [ "$entry" == "" ]
   then
     echo " File seems corrupted. Skip it."
     echo " # CP # t2tools.py --action rm --source $oldFile"
     continue
   fi
   newFile=`echo $oldFile | sed -e 's@crab_0.*/@@' -e 's@_tmp.root@.root@'`
   newEntry=`echo $entry | sed -e 's@crab_0.*/@@' -e 's@_tmp.root@.root@'`
   #echo "t2tools.py --action mv --source $oldFile --target $newFile"
   t2tools.py --action mv --source $oldFile --target $newFile > /dev/null
   echo "   adding: $newEntry"
   echo $newEntry >> RawFiles.00.$$

done
cat RawFiles.00.$$ >> $cata/$dset/RawFiles.00
rm  RawFiles.00.$$

extractCatalog.py  --dataset=$dset --mitCfg=$mitcfg --version=$version --compact > /dev/null
generateCatalog.py --rawFile=$cata/$dset --nFilesPerSet=20                       > /dev/null
