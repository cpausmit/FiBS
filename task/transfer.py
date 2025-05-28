#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Transfer exactly one file from FNAL to MIT T3.
#
#                                                                             Ch.Paus (Jul 17, 2020)
#---------------------------------------------------------------------------------------------------
import os,sys,re,socket,datetime,time

# default
SERVER_CERN = "root://eoscms.cern.ch//eos/cms/store/group/phys_heavyions/jdlang"
SERVER_MIT = "root://xrootd.cmsaf.mit.edu//store/user/jdlanfg/public"
#SERVER_CERN = "file:///ceph/submit/data/group/cms"
#SERVER_CERN = "gsiftp://eoscmsftp.cern.ch//eos/cms"
#SERVER_CERN = "file:///mnt/hadoop/cms"#
#SERVER_MIT = "root://t2dsk0011.cmsaf.mit.edu/"
#SERVER_MIT = "file:///mnt/hadoop/cms"

#---------------------------------------------------------------------------------------------------
#  H E L P E R S 
#---------------------------------------------------------------------------------------------------

def showSetup(status):
    if   status == 'start':
        print("\n=-=-=-= Show who and where we are =-=-=-=\n")
        print(" Script:    %s"%(os.path.basename(__file__)))
        print(" Arguments: %s"%(" ".join(sys.argv[1:])))
        print(" ")
        print(" user executing: " + os.getenv('USER','unknown user'))
        print(" running on    : %s"%(socket.gethostname()))
        print(" running in    : %s"%(os.getcwd()))
        print(" start time    : %s"%(str(datetime.datetime.now())))
    elif status == 'end':
        print(" end   time    : %s"%(str(datetime.datetime.now())))
    else:
        print(" now   time    : %s (%s)"%(str(datetime.datetime.now()),str(status)))
    print(" ")

    return

def exeCmd(cmd,debug=0):
    # execute a given command and show what is going on

    rc = 0

    if debug>1:
        print(' =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
    if debug>0:
        print(' =Execute:  %s'%(cmd))
    rc = os.system(cmd) ##print ' !! DISABLED EXECUTION !! '
    if debug>1:
        print(' =E=N=D=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n')
    return rc

def extractLfn(fullFile,debug=0):
    # extract the lfn rom the given file name
    if debug>1:
        print(" File: %s"%(fullFile))
    try:
        lfn = fullFile[fullFile.index('/store'):]
    except:
        lfn = fullFile

    return lfn

def transferFile(lfn,debug=0):
    # execute the file transfer

    n_try = 0
    max_try = 5
    
    #cmd = "gfal-copy -p %s%s %s%s"%(SERVER_CERN,lfn,SERVER_MIT,lfn) 
    cmd = "xrdcp -s %s%s %s%s"%(SERVER_CERN,lfn,SERVER_MIT,lfn) 
    print("CMD: %s"%(cmd))
    
    while (n_try<max_try):
        rc = exeCmd(cmd,debug)
        if rc == 0:
            print(" transfer worked (%s)."%(lfn))
            break
        else:
            print(" transfer FAILED with %d (%s)."%(rc,lfn))
        n_try += 1

    return rc

def removeRemainder(lfn,debug=0):
    # remove reaminder from failed transfer

    cmd = "gfal-rm %s%s"%(SERVER_MIT,lfn) 
    rc = exeCmd(cmd,debug)
    if rc == 0:
        print(" removed remainder: %s."%(lfn))
    else:
        print(" removing remainder FAILED (rc=%s): %s."%(rc,lfn))

    return rc

def existFile(lfn,debug=0):
    # check if file exists already

    cmd = "gfal-ls -l %s%s"%(SERVER_MIT,lfn) 
    rc = exeCmd(cmd,debug)
    if rc == 0:
        print(" file listed successfully: %s."%(lfn))
    else:
        print(" file listing FAILED (rc=%s): %s."%(rc,lfn))

    return rc

#---------------------------------------------------------------------------------------------------
#  M A I N
#---------------------------------------------------------------------------------------------------
debug = 2

# make announcement
showSetup('start')

# make sure we have at least one parameter
if len(sys.argv)<2:
    print('\n ERROR - Missing file name as parameter.\n')
    showExit(1)

# read command line parameters
fullFile = " ".join(sys.argv[1:])

# make sure to trim the input file if needed (want to go back to lfn = /store/...)
lfn = extractLfn(fullFile,debug)

# show the certificate
exeCmd("voms-proxy-init --valid 168:00 -voms cms",debug)
exeCmd("voms-proxy-info -all",debug)

# download the file to local
rc = existFile(lfn,debug)
if rc == 0:
    print("\n Our work is done, file exists already.\nEXIT\n")
    showSetup(rc)
    sys.exit(rc)

# download the file to local
rc = transferFile(lfn,debug)
if rc != 0:
    print("\n File transfer failed. EXIT!\n Cleanup potential remainders.")
    removeRemainder(lfn,debug)
    showSetup(rc)
    sys.exit(rc)

# make announcement
showSetup('end')
sys.exit(0)
