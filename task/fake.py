#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Upload exactly one file to dropbox.
#
#                                                                             Ch.Paus (Sep 30, 2015)
#---------------------------------------------------------------------------------------------------
import os,sys,re,socket,datetime,time
#---------------------------------------------------------------------------------------------------
#  H E L P E R S 
#---------------------------------------------------------------------------------------------------

def showSetup():
    print "\n=-=-=-= Show who and where we are =-=-=-=\n"
    print " Script:    %s"%(os.path.basename(__file__))
    print " Arguments: %s"%(" ".join(sys.argv[1:]))
    print " "
    print " start time    : %s"%(str(datetime.datetime.now()))
    print " user executing: " + os.getenv('USER','unknown user')
    print " running on    : %s"%(socket.gethostname())
    print " executing in  : %s"%(os.getcwd())
    print " "

    return

#---------------------------------------------------------------------------------------------------
#  M A I N
#---------------------------------------------------------------------------------------------------

# make announcement
showSetup()
time.sleep(10)

showSetup()
time.sleep(10)

showSetup()
time.sleep(10)

showSetup()
time.sleep(10)

sys.exit(0)
