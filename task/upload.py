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

    # See whether we are setup
    base = os.environ.get('PYCOX_BASE')
    if base=='':
        print '\n ERROR -- PYCOX is not setup PYCOX_BASE environment not set.\n'
        sys.exit(1)

    return

def exeCmd(cmd,debug=0):
    # execute a given command and show what is going on

    if debug>1:
        print ' =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
    if debug>0:
        print ' =Execute:  %s'%(cmd)
    rc = os.system(cmd)
    if debug>1:
        print ' =E=N=D=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n'
    return rc

def reviewFileName(fullFile,debug=0):
    # execute a given command and show what is going on

    file = fullFile
    if fullFile.startswith('/cms/store'):
        file = fullFile.replace('/cms/store','/store',1)
        if debug>1:
            print ' Trimming input file name: %s -> %s'%(fullFile,file)

    return file

def pullFileToLocal(fullFile,debug=0):
    # execute a given command and show what is going on

    baseFile = (fullFile.split("/")).pop()

    # default
    SERVER = "se01.cmsaf.mit.edu"
    cmd = "lcg-cp -D srmv2 -b srm://" + SERVER + ":8443/srm/v2/server?SFN=/mnt/hadoop/cms" \
        + fullFile + " file:///tmp/" + baseFile 

    if True:
        unit = int(time.time()) % 10 + 1
        #SERVER = "xrootd.unl.edu"
        SERVER = "xrootd%1d.cmsaf.mit.edu"%(unit)
        cmd = "xrdcp -s root://" + SERVER + "/" + fullFile + " /tmp/" + baseFile 

    rc = exeCmd(cmd,debug)

    if rc == 0:
        print " local download worked."
    else:
        print " local download failed (rc=%s)."%(rc)

    return rc

def makeDbxDir(fullFile,debug=0):
    # make the remote directory

    f = fullFile.split("/")
    f.pop()
    dir = '/'.join(f)
    rc = exeCmd("$MY_PYTHON $PYCOX_BASE/pycox.py --action=mkdir --source=/cms" + dir)

    if rc == 0:
        print " make remote directory worked."
    else:
        print " make remote directory failed (rc=%s)."%(rc)

    return rc

def uploadFile(fullFile,debug=0):
    # make the remote directory

    baseFile = (fullFile.split("/")).pop()
    rc = exeCmd("$MY_PYTHON $PYCOX_BASE/pycox.py --action=up" \
                    + " --source=/tmp/%s --target=/cms%s"%(baseFile,fullFile))

    if rc == 0:
        print " upload worked."
    else:
        print " upload failed (rc=%s)."%(rc)

    return rc

#---------------------------------------------------------------------------------------------------
#  M A I N
#---------------------------------------------------------------------------------------------------
debug = 2

# make announcement
showSetup()

# make sure we have at least one parameter
if len(sys.argv)<2:
    print '\n ERROR - Missing file name as parameter.\n'
    sys.exit(1)

# read command line parameters
fullFile = sys.argv[1]
baseFile = (fullFile.split("/")).pop()

# make sure to trim the input file if needed (want to go back to lfn = /store/...)
fullFile = reviewFileName(fullFile,debug)

# show the certificate
exeCmd("voms-proxy-init --valid 168:00 -voms cms",debug)
exeCmd("voms-proxy-info -all",debug)

# download the file to local
rc = pullFileToLocal(fullFile,debug)
if rc != 0:
    print "\n Local file download failed. EXIT!\n Cleanup potential remainders."
    exeCmd("rm -f /tmp/%s"%(baseFile))
    sys.exit(rc)

# prepare the directory on remote site
makeDbxDir(fullFile,debug)
if rc != 0:
    print "\n Making dropbox directory failed. EXIT!\n Cleanup potential remainders."
    exeCmd("rm -f /tmp/%s"%(baseFile))
    sys.exit(rc)

# upload
uploadFile(fullFile,debug)

# make sure to cleanup
exeCmd("rm -f /tmp/%s"%(baseFile))

sys.exit(0)
