#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Upload exactly one file to the mit tape system.
#
#                                                                             Ch.Paus (Feb 04, 2022)
#---------------------------------------------------------------------------------------------------
import os,sys,re,socket,datetime,time

STARTPOINT = "gsiftp://se01.cmsaf.mit.edu:2811/cms"
ENDPOINT = "gsiftp://tapesrmcms.nese.rc.fas.harvard.edu:2811/cms"

#---------------------------------------------------------------------------------------------------
#  H E L P E R S 
#---------------------------------------------------------------------------------------------------

def showSetup():
    print("\n=-=-=-= Show who and where we are =-=-=-=\n")
    print(" Script:    %s"%(os.path.basename(__file__)))
    print(" Arguments: %s"%(" ".join(sys.argv[1:])))
    print(" ")
    print(" start time    : %s"%(str(datetime.datetime.now())))
    print(" user executing: " + os.getenv('USER','unknown user'))
    print(" running on    : %s"%(socket.gethostname()))
    print(" executing in  : %s"%(os.getcwd()))
    print(" ")

    return

def exeCmd(cmd,debug=0):
    # execute a given command and show what is going on

    if debug>1:
        print(' =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
    if debug>0:
        print(' =Execute:  %s'%(cmd))
    rc = os.system(cmd)
    if debug>1:
        print(" RC: %d"%(int(rc)))
        print(' =E=N=D=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n')
    return rc

def reviewFileName(fullFile,debug=0):
    # execute a given command and show what is going on

    file = fullFile
    if fullFile.startswith('/cms/store'):
        file = fullFile.replace('/cms/store','/store',1)
        if debug>1:
            print(' Trimming input file name: %s -> %s'%(fullFile,file))

    return file

def uploadFile(fullFile,debug=0):
    # make the remote directory

    baseFile = (fullFile.split("/")).pop()
    rc = exeCmd("source /cvmfs/grid.cern.ch/centos7-ui-test/etc/profile.d/setup-c7-ui-example.sh; which gfal-copy; gfal-copy -p %s%s %s%s"%(STARTPOINT,fullFile,ENDPOINT,fullFile),debug)

    if rc == 0:
        print(" upload worked.")
    else:
        print(" upload failed (rc=%s)."%(rc))

    return rc

#---------------------------------------------------------------------------------------------------
#  M A I N
#---------------------------------------------------------------------------------------------------
debug = 2

# make announcement
showSetup()

# make sure we have at least one parameter
if len(sys.argv)<2:
    print('\n ERROR - Missing file name as parameter.\n')
    sys.exit(1)

# read command line parameters
fullFile = sys.argv[1]
baseFile = (fullFile.split("/")).pop()

# make sure to trim the input file if needed (want to go back to lfn = /store/...)
fullFile = reviewFileName(fullFile,debug)

# show the certificate
exeCmd("voms-proxy-init --valid 168:00 -voms cms",debug)
exeCmd("voms-proxy-info -all",debug)

# upload
rc = uploadFile(fullFile,debug)

# make sure to cleanup
exeCmd("rm -f /tmp/%s"%(baseFile))

sys.exit(rc)
