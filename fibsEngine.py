#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#
# This is the engine that we can start on a given machine and it will start activity as instructed.
#
#                                                                        v0 - April 1, 2016 - C.Paus
#---------------------------------------------------------------------------------------------------
import os,sys,getopt,re,ConfigParser,time,socket
import dblock

#===================================================================================================
#  H E L P E R S
#===================================================================================================
def testLocalSetup(list,debug=0):
    # The local setup needs a number of things to be present. Make sure all is there, or complain.

    # See whether we are setup
    base = os.environ.get('FIBS_BASE')
    if base=='':
        print '\n ERROR -- FiBS is not setup FIBS_BASE environment not set.\n'
        sys.exit(1)

    if list=='':
        print '\n ERROR -- FiBS needs a list of files to consider.\n'
        sys.exit(1)

    return

def establishLock(debug):
    # check if so someone is locking and if not, establish a lock

    lock = None
    while not lock:
        lock = dblock.dblock(os.environ.get('FIBS_WORK')+'/lock',True).acquire()
        if not lock:
            time.sleep(1)

    return lock

def readList(listFile,debug):
    # read the list of files into memory

    with open(os.environ.get('FIBS_WORK')+'/'+listFile,'r') as fileH:
        fileList = [line.rstrip('\n') for line in fileH]

    return fileList

def writeList(listFile,fileList,debug):
    # write the list of files from memory back to the file

    with open(os.environ.get('FIBS_WORK')+'/'+listFile,'w') as fileH:
        for file in fileList:
            fileH.write(file + '\n')

    return fileList


def getFiles(fileList,nFiles,debug):
    # take out the first nFiles entries of the list

    n = 0
    files = []
    for file in fileList:
        files.append(file)
        n += 1
        if n >= nFiles: # we got nFiles out
            break

    return (files,fileList[nFiles:])

def pullFilesFromList(listFile,nFiles,debug):
    # pull a given number of files from a list of files that are stored in a file the tricky bit
    # is that there are several asyncronous processes running and a lock has to be established

    # get the lock
    lock = establishLock(debug)

    # read the file list into memory
    fileList = readList(listFile,debug)
    
    # get files to work on
    (files,fileList) = getFiles(fileList,nFiles,debug)

    # now write the remainig list back to the file
    writeList(listFile,fileList,debug)

    # finally we can release the lock
    lock.release()

    return files

#===================================================================================================
#  M A I N
#===================================================================================================
# Define string to explain usage of the script
usage =  " Usage: fibs.py   --task=<script to run>\n"
usage += "                  --list=<list of file to consider>\n"
usage += "                [ --debug=0 ]             <-- see various levels of debug output\n"
usage += "                [ --exec ]                <-- add this to execute all actions\n"
usage += "                [ --help ]\n"

# Define the valid options which can be specified and check out the command line
valid = ['configFile=','task=','list=','debug=','exec','help']
try:
    opts, args = getopt.getopt(sys.argv[1:], "", valid)
except getopt.GetoptError, ex:
    print usage
    print str(ex)
    sys.exit(1)

# --------------------------------------------------------------------------------------------------
# Get all parameters for the production
# --------------------------------------------------------------------------------------------------
# Set defaults for each command line parameter/option
configFile = os.environ.get('FIBS_BASE') + '/' + 'fibs.cfg'
testFile = os.environ.get('HOME') + '/' + '.fibs.cfg'
if os.path.isfile(testFile):
    configFile = testFile

list = ''
nFiles = 1
exe = False
debug = 0

# Read new values from the command line
for opt, arg in opts:
    if   opt == "--help":
        print usage
        sys.exit(0)
    elif opt == "--list":
        list = arg
    elif opt == "--configFile":
        configFile = arg
    elif opt == "--debug":
        debug = int(arg)
    elif opt == "--exec":
        exe = True

# keeping track of the hostname
hostname = socket.gethostname()

# inspecting the local setup
#---------------------------
testLocalSetup(list,debug)

# reading detailed configurations
#--------------------------------
config = ConfigParser.RawConfigParser()
config.read(configFile)

# get our parameters as needed
base = os.environ.get('FIBS_BASE')
task = config.get('general','task')
outerr = config.get('io','outerr')

# make sure we have the output directory
os.system("mkdir -p " + outerr)

# Grab files from the list (first lock, re-write and unlock)
#-----------------------------------------------------------
# -- quit when job is done
#files = ['empty']
#while len(files) > 0:

# -- stay in there and let job develop
while True:

    files = pullFilesFromList(list,nFiles,debug)
    print files

    for file in files:

        # get base file
        baseFile = (file.split('/')).pop()

        # execute our task
        cmd = base + '/task/' + task + ' ' + file \
            + ' 1> ' + outerr + '/' + baseFile + '-' + hostname + '.out' \
            + ' 2> ' + outerr + '/' + baseFile + '-' + hostname + '.err'
        
        os.system(cmd)
        
sys.exit(0)
