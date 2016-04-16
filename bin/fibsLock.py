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
def establishLock(debug):
    # check if so someone is locking and if not, establish a lock

    lock = None
    while not lock:
        lock = dblock.dblock(os.environ.get('FIBS_WORK')+'/lock',True).acquire()
        if not lock:
            time.sleep(1)

    return lock

#===================================================================================================
#  M A I N
#===================================================================================================
# Define string to explain usage of the script
usage =  " Usage: fibsLock.py [ --debug=0 ]             <-- see various levels of debug output\n"
usage += "                    [ --help ]\n\n"

# Define the valid options which can be specified and check out the command line
valid = ['debug=','help']
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
debug = 0

# Read new values from the command line
for opt, arg in opts:
    if   opt == "--help":
        print usage
        sys.exit(0)
    elif opt == "--debug":
        debug = int(arg)

# keeping track of the hostname
hostname = socket.gethostname()

lock = establishLock(debug)
answer = raw_input("Type return when done: ")
lock.release()
        
sys.exit(0)
