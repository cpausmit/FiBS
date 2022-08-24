#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#
# This is the engine that we can start on a given machine and it will start activity as instructed.
#
#
#                                                                        v0 - April 1, 2016 - C.Paus
#---------------------------------------------------------------------------------------------------
import os,sys,getopt,re,time,socket
#import configparser as ConfigParser
import ConfigParser

import dblock

#===================================================================================================
#  H E L P E R S
#===================================================================================================
def testLocalSetup(debug=0):
    # The local setup needs a number of things to be present. Make sure all is there, or complain.

    # See whether we are setup
    base = os.environ.get('FIBS_BASE')
    if base == '':
        print('\n fibsEngine: ERROR -- FiBS is not setup FIBS_BASE environment not set.\n')
        sys.exit(1)

    return

def establishLock(task,debug):
    # check if so someone is locking and if not, establish a lock

    lock = None
    while not lock:
        lock = dblock.dblock(os.environ.get('FIBS_WORK') + '/' + task,True).acquire()
        if not lock:
            time.sleep(1)

    return lock

def readList(listFile,debug):
    # read the list of files into memory
    tmp = []
    if os.path.exists(os.environ.get('FIBS_WORK')+'/'+listFile):
        with open(os.environ.get('FIBS_WORK')+'/'+listFile) as fH:
            tmp = fH.read().split('\n')

    # make sure to clean list from invalid entries
    fileList = []
    for f in tmp:
        if f.strip() != '':
            fileList.append(f)

    if debug>0:
        print(' fibsEngine: readList -- Found %d files.'%(len(fileList)))
        print(fileList)

    return fileList

def writeList(listFile,fileList,debug):
    # write the list of files from memory back to the file

    with open(os.environ.get('FIBS_WORK')+'/'+listFile,'w') as fH:
        for file in fileList:
            if file != '':   # avoid empty lines
                fH.write(file + '\n')

    if debug>0:
        print(' fibsEngine: writeList -- Found %d files.'%(len(fileList)))
        print(fileList)

    return fileList

def getFiles(fileList,nentries,debug):
    # take out the first nentries from the list

    n = 0
    files = []
    for file in fileList:
        files.append(file)
        n += 1
        if n >= nentries: # we got nentries out
            break

    return (files,fileList[nentries:])

def pullFilesFromList(task,listFile,nentries,debug):
    # pull a given number of files from a list of files that are stored in a file the tricky bit
    # is that there are several asyncronous processes running and a lock has to be established

    # get the lock
    lock = establishLock(task,debug)

    # read the file list into memory
    fileList = readList(listFile,debug)
    
    # get files to work on
    (files,fileList) = getFiles(fileList,nentries,debug)

    # now write the remainig list back to the file
    writeList(listFile,fileList,debug)

    # finally we can release the lock
    lock.release()

    return files

#===================================================================================================
#  M A I N
#===================================================================================================
# Define string to explain usage of the script
usage =  " Usage: fibsEngine.py   --configFile=<file with full config>\n"
usage += "                        --instance=0            <-- the instance on this machine\n"
usage += "                      [ --debug=0 ]             <-- see various levels of debug output\n"
usage += "                      [ --help ]\n"

# Define the valid options which can be specified and check out the command line
valid = ['configFile=','instance=','debug=','help']
try:
    opts, args = getopt.getopt(sys.argv[1:], "", valid)
except getopt.GetoptError as ex:
    print(usage)
    print(str(ex))
    sys.exit(1)

# --------------------------------------------------------------------------------------------------
# Get all parameters for the production
# --------------------------------------------------------------------------------------------------
# Set defaults for each command line parameter/option

# keeping track of the hostname
hostname = socket.gethostname()
nentries = 1
instance = '0'
debug = 2
configFile = ''

# Read new values from the command line
for opt, arg in opts:
    if   opt == "--help":
        print(usage)
        sys.exit(0)
    elif opt == "--configFile":
        configFile = os.environ.get('FIBS_CFGS') + '/' + arg + '.cfg'
    elif opt == "--instance":
        instance = arg
    elif opt == "--debug":
        debug = arg


# reading detailed configurations
#--------------------------------
config = ConfigParser.RawConfigParser()
config.read(configFile)
task = config.get('general','task')
if config.has_option('general','nentries'):
    nentries = int(config.get('general','nentries'))
list = config.get('general','list')

# get our environment parameters as needed
base = os.environ.get('FIBS_BASE')
outerr = os.environ.get('FIBS_LOGS') + '/' + config.get('io','outerr')
taskdir = os.environ.get('FIBS_TASK')
log = outerr + '-' + hostname + '_' + instance + '.log'

# inspecting the local setup
#---------------------------
testLocalSetup(debug)

# make sure we have the output directory
os.system("mkdir -p " + outerr)

# make sure now to capture all input and open and close to keep it up to date
os.system("touch " + log)
handleStdout = sys.stdout
sys.stdout = open(log,'a')

# Grab files from the list (first lock, re-write and unlock)
#-----------------------------------------------------------

# -- testing with a limited duration queue (engine will exit once work is done)
# files = ['0','1']
# while len(files) > 0:

# -- stay in there and let job develop
while True:

    files = pullFilesFromList(task,list,nentries,debug)
    print(files)

    cmd = 'mkdir -p ' + outerr
    if debug>0:
        print(" fibsEngine: Make dir  %s"%(cmd))
    os.system(cmd)

    for file in files:

        if debug>0:
            print(" fibsEngine: processing  %s"%(file))

        # get base file
        baseFile = (file.split('/')).pop()
        baseFile = baseFile.replace(' ','%')

        # execute our task
        cmd = taskdir + '/' + task + ' ' + file \
            + ' 1> ' + outerr + '/' + baseFile + '-' + hostname + '_' + instance + '.out' \
            + ' 2> ' + outerr + '/' + baseFile + '-' + hostname + '_' + instance + '.err'
        
        if file != '':
            print(' fibsEngine: next task: %s'%(cmd))
            os.system(cmd)
        else:
            print(' fibsEngine: there is no work here to be done. (sleep 5)')
            time.sleep(5)

    # when the list is empty take some time to ask for more
    if len(files) == 0:
        if debug > 1:
            print('\n fibsEngine: List is empty: waiting for 10 secs.')
        time.sleep(10)
  
sys.exit(0)
