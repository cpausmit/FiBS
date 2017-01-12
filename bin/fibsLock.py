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
def establishLock(task,debug):
    # check if so someone is locking and if not, establish a lock

    lock = None
    while not lock:
        lock = dblock.dblock(os.environ.get('FIBS_WORK') + '/' + task,True).acquire()
        if not lock:
            time.sleep(1)

    return lock

#===================================================================================================
#  M A I N
#===================================================================================================
# Define string to explain usage of the script
usage =  " Usage: fibsLock.py   --configFile=<file with full config>\n"
usage += "                    [ --cmd='' ]          <-- execute OS command inside lock\n"
usage += "                    [ --seconds=-1 ]      <-- keep lock for a fixed number of seconds\n"
usage += "                    [ --debug=0 ]         <-- see various levels of debug output\n"
usage += "                    [ --help ]\n\n"

# Define the valid options which can be specified and check out the command line
valid = ['configFile=','cmd=','seconds=','debug=','help']
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
seconds = -1
debug = 0
configFile = ''
cmd = ''

# Read new values from the command line
for opt, arg in opts:
    if   opt == "--help":
        print usage
        sys.exit(0)
    elif opt == "--configFile":
        configFile = arg
    elif opt == "--seconds":
        seconds = int(arg)
    elif opt == "--cmd":
        cmd = arg
    elif opt == "--debug":
        debug = int(arg)

# make sure we have a working setup

if not os.path.exists(configFile):
    print '\n ERROR - no configuration specified.\n'
    print usage
    sys.exit(1)

if cmd == '':
    print '\n ERROR - no shell command specified.\n'
    print usage
    sys.exit(1)

# reading detailed configurations
#--------------------------------
config = ConfigParser.RawConfigParser()
config.read(configFile)

# get our parameters as needed
task = config.get('general','task')

# keeping track of the hostname
hostname = socket.gethostname()

# establish lock
lock = establishLock(task,debug)

# now consider our options
if   cmd != '':
    print ' Executing: ' + cmd
    os.system(cmd)
elif seconds >= 0:
    time.sleep(seconds)
else:
    answer = raw_input("Type return when done: ")

# release the lock
lock.release()
print '\n Exiting.'
        
sys.exit(0)
