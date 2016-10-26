#!/usr/bin/env python
import os,re,pprint,subprocess,sys,datetime,MySQLdb

Db = MySQLdb.connect(read_default_file="/etc/my.cnf",read_default_group="mysql",db="Bambu")
Cursor = Db.cursor()

usage = "\n   usage:  checkFile.py  <file> \n"

#===================================================================================================
#  H E L P E R S
#===================================================================================================
def catalogFile(file):
    # perfrom cataloging operation on one file (return the entry)

    cmd = 'catalogFile.sh ' + file
    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode

    entry = ''
    lines = out.split("\n")
    for line in lines:
        if 'XX-CATALOG-XX 0000' in line:
            entry = line.replace('XX-CATALOG-XX 0000 ','')

    return entry

def getName(file):
    # extract the unique file name

    f = file.split('/')
    fileName = (f.pop()).replace('.root','')
    fileName = fileName.replace('_tmp','')         # maybe this is a temporary file

    return fileName

def getFinalFile(file):
    # extract the unique file name

    finalFile = file

    if 'crab_' in file:
        f = file.split('/')
        tmp = f[-1].replace('_tmp','') 
        finalFile = "/".join(f[:-2])
        finalFile = finalFile + '/' + tmp
        
    return finalFile

def getRequestId(file):
    # extract the unique request id this file is part of

    requestId = -1
    datasetId = -1

    f = file.split('/')
    if 'crab_' in file:
        dataset = f[-3]
        version = f[-4]
        mitcfg = f[-5]
    else:
        dataset = f[-2]
        version = f[-3]
        mitcfg = f[-4]

    # decode the dataset
    f = dataset.split('+')
    process = f[0]
    setup = f[1]
    tier = f[2]

    sql = "select RequestId, Datasets.DatasetId from Requests inner join Datasets on " \
        + " Datasets.DatasetId = Requests.DatasetId where " \
        + " DatasetProcess = '%s' and DatasetSetup='%s' and DatasetTier='%s'"%(process,setup,tier) \
        + " and RequestConfig = '%s' and RequestVersion = '%s'"%(mitcfg,version)

    try:
        # Execute the SQL command
        Cursor.execute(sql)
        results = Cursor.fetchall()
    except:
        print 'ERROR(%s) - could not find request id.'%(sql)

    # found the request Id
    for row in results:
        requestId = int(row[0])
        datasetId = int(row[1])

    return (requestId, datasetId)

def numberOfEventsInEntry(entry):
    # extract the number of events in a given catalog entry

    f = entry.split(" ")
    nEvents = -1
    if len(f)>1: 
        nEvents = int(f[1])

    return nEvents

def loadEnv():
    # make sure to setup the environment
    rc = 0
    base = os.environ.get('FIBS_BASE')
    if os.path.exists(base + '/config/checkFile.bash'):
        cmd = 'bash -c ' + base + '/config/checkFile.bash'
        list = cmd.split(" ")
        p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (out, err) = p.communicate()
        rc = p.returncode
        for line in out.split("\n"):
            (key, _, value) = line.partition("=")
            os.environ[key] = value
        print ' INFO - special environment for checkFile.py was loaded.'
    else:
        print ' INFO - special environment needed.'

    return rc

def makeDatabaseEntry(requestId,fileName,nEvents):

    sql = "insert into Files(RequestId,FileName,NEvents) " \
        + " values(%d,'%s',%d)"%(requestId,fileName,nEvents)
    print ' SQL: ' + sql
    try:
        # Execute the SQL command
        Cursor.execute(sql)
    except:
        print 'ERROR(%s) - could not insert new file.'%(sql)

def getNEventsLfn(datasetId,fileName):

    nEvents = -1

    sql = "select FileName, PathName, NEvents from Lfns where DatasetId = %d and FileName = '%s'"\
        %(datasetId,fileName)
    try:
        # Execute the SQL command
        Cursor.execute(sql)
        results = Cursor.fetchall()
    except:
        print 'ERROR(%s) - could not find request id.'%(sql)

    # found the request Id
    for row in results:
        name = row[0]
        path = row[1]
        nEvents = int(row[2])

    return nEvents

#===================================================================================================
#  M A I N
#===================================================================================================
# make sure command line is complete
if len(sys.argv) < 1:
    print " ERROR -- " + usage
    sys.exit(1)

# make sure the environment is what we want
loadEnv()

# command line variables
file = sys.argv[1]
print " INFO - checkFile.py %s"%(file)     
            
# doing the cataloging here
entry = catalogFile(file)
nEvents = numberOfEventsInEntry(entry)

print ' CATALOG: %d -- %s'%(nEvents,file)

# find all relevant Ids
fileName = getName(file)
(requestId,datasetId) = getRequestId(file)

# find corresponding lfn
nEventsLfn = getNEventsLfn(datasetId,fileName)

print ' Compare: %d [lfn] and %d [output]'%(nEventsLfn,nEvents)

if nEvents == nEventsLfn and nEvents>0:
    # now move file to final location
    finalFile = getFinalFile(file)
    if 'crab_' in file:
        cmd = "t2tools.py --action mv --source " +  file + " --target " + finalFile + " >/dev/null"
        print ' MOVE: ' + cmd
        os.system(cmd)
    
    # add a new catalog entry
    makeDatabaseEntry(requestId,fileName,nEvents)

else:
    print ' ERROR: event counts disagree or not positive (LFN %d,File %d). EXIT!'%(nEventsLfn,nEvents)