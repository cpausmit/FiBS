#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Fake some activity and produce output.
#
#                                                                             Ch.Paus (Sep 30, 2015)
#---------------------------------------------------------------------------------------------------
import os,sys,re,socket,datetime,time

#---------------------------------------------------------------------------------------------------
#  H E L P E R S 
#---------------------------------------------------------------------------------------------------
def showSetup(firstTime,fHandle):
    if firstTime:
        fileH.write("\n=-=-=-= Show who and where we are =-=-=-=\n\n")
        fileH.write(" Script:    %s\n"%(os.path.basename(__file__)))
        fileH.write(" Arguments: %s\n"%(" ".join(sys.argv[1:])))
        fileH.write(" \n")
        fileH.write(" start time    : %s\n"%(str(datetime.datetime.now())))
    else:
        fileH.write(" time now      : %s\n"%(str(datetime.datetime.now())))

    fileH.write(" user executing: " + os.getenv('USER','unknown user') + "\n")
    fileH.write(" running on    : %s\n"%(socket.gethostname()))
    fileH.write(" executing in  : %s\n"%(os.getcwd()))
    fileH.write(" arguments:      %s\n"%(" ".join(sys.argv[1:])))
    fileH.write(" \n")

    return

def showSetupStd():
    print(" user executing: " + os.getenv('USER','unknown user'))
    print(" running on    : %s"%(socket.gethostname()))
    print(" executing in  : %s"%(os.getcwd()))
    print(" arguments:      %s"%(" ".join(sys.argv[1:])))
    print(" time now      : %s"%(str(datetime.datetime.now())))
    print(" ")

    return

#---------------------------------------------------------------------------------------------------
#  M A I N
#---------------------------------------------------------------------------------------------------

# make announcement
firstTime = True
nLoop = 0
while nLoop<4:

    # if firstTime:
    #     fileH = open('/home/cmsprod/cms/logs/fibs/fake.log','w')
    # else:
    #     fileH = open('/home/cmsprod/cms/logs/fibs/fake.log','a')
    # showSetup(firstTime,fileH)
    # fileH.close()
    # firstTime = False

    showSetupStd()
    time.sleep(4)

    nLoop +=1


sys.exit(0)
