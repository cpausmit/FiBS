#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Download exactly one file from a given xrootd location to MIT T3.
#
#                                                                             Ch.Paus (Mar 25, 2021)
#---------------------------------------------------------------------------------------------------
import os,sys,re,socket,datetime,time

# default
T3_BASE = "/ceph/submit/data/group/cms"
#T3_BASE = "/mnt/hadoop/cms"
#T3_BASE= "root://t3serv017.mit.edu/"

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
        print(" error time    : %s (%s)"%(str(datetime.datetime.now()),str(status)))
    print(" ")

    return

def exeCmd(cmd,debug=0):
    # execute a given command and show what is going on

    rc = 0

    if debug>1:
        print(' =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
    if debug>0:
        print(' =Execute:  %s'%(cmd))
    rc = os.system(cmd) ##print(' !! DISABLED EXECUTION !! ')
    if debug>1:
        print( ' =E=N=D=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n')
    return rc

def extractLfn(fullFile,debug=0):
    # extract the lfn rom the given file name
    if debug>1:
        print(" File: %s"%(fullFile))
    lfn = fullFile[fullFile.index('/store'):]
    #lfn = lfn.replace("wangz","paus")        # for files from Qier

    return lfn

def downloadFile(file_xrootd,lfn,debug=0):
    # execute the file download

    cmd = "xrdcp root://xrootd.cmsaf.mit.edu/%s %s%s"%(lfn,T3_BASE,lfn) 
    print("CMD: %s"%(cmd))
    rc = exeCmd(cmd,debug)
    if rc == 0:
        print(" download worked (%s)."%(lfn))
    else:
        print(" download FAILED with %d (%s)."%(rc,lfn))

    return rc

def removeRemainder(lfn,debug=0):
    # remove remainder from failed download

    cmd = "rm %s%s"%(T3_BASE,lfn) 
    rc = exeCmd(cmd,debug)
    if rc == 0:
        print(" removed remainder: %s%s."%(T3_BASE,lfn))
    else:
        print(" removing remainder FAILED (rc=%s): %s."%(rc,lfn))

    return rc

def existFile(lfn,debug=0):
    # check if file exists already

    cmd = "ls -l %s%s >& /dev/null"%(T3_BASE,lfn) 
    rc = exeCmd(cmd,debug)
    if rc == 0:
        print(" file listed successfully: %s."%(lfn))
    else:
        print(" file listing FAILED (rc=%s) so we need to download: %s."%(rc,lfn))

        dir = "/".join(lfn.split("/")[:-1])
        print("DIR: %s%s"%(T3_BASE,dir))
    
        cmd = "ls -l %s%s >& /dev/null"%(T3_BASE,dir) 
        tmprc = exeCmd(cmd,debug)
        if tmprc == 0:
            print(" directory exists: %s."%(lfn))
        else:
            cmd = "mkdir -p %s%s >& /dev/null"%(T3_BASE,dir) 
            tmprc = exeCmd(cmd,debug)
            print(" directory created (RC=%d): %s."%(int(tmprc),lfn))
        

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
    showSetup('end')
    sys.exit(rc)

# download the file to local
rc = downloadFile(fullFile,lfn,debug)
if rc != 0:
    print("\n File download failed. EXIT!\n Cleanup potential remainders.")
    removeRemainder(lfn,debug)
    showSetup(rc)
    sys.exit(rc)

# make announcement
showSetup('end')
sys.exit(0)
