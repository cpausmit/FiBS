#!/usr/bin/env python
#==================================================================================================
#
# Script to remove all downloading log files and create a record of what happened when.
#
#==================================================================================================
import os,sys,subprocess
import time,datetime
import atom

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mlp

from optparse import OptionParser

PATTERN = '%a %b %d %I:%M:%S %p %Z %Y'
PATTERN_B = '%a %b %d %H:%M:%S %Z %Y'

RECORD = {}
PLOT_FIRST = True

TASK = 'download'
DEBUG = 0


def appendRecord(record):
    # append the record to the already existing one
    print(" Appending latest record to existing file (%d)"%(len(record)))
    with open(f"{options.base}/{TASK}Activity.db","a") as f:
        for key in record:
            f.write('%s,%s\n'%(key,record[key]))
    return

def findAllJobStubs(dir,debug=0):
    # find all job file stubs (without .err/.out extensions) to analyze
    cmd = "cd %s; ls -1rt"%(dir)
    if debug > 0:
        print(" CMD: " + cmd)
    
    p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode
    
    if debug > 0:
        print("\n\n RC : " + str(rc))
        print("\n\n OUT:\n" + out.decode())
        print("\n\n ERR:\n" + err.decode())
        
    stubs = []
    for line in out.decode().split('\n'):
        if '.err' in line:
            stubs.append(line.replace('.err',''))

    print(' Number of all jobs found: %d'%(len(stubs)))

    return stubs

def reviewStub(record,options,stub):
    
    if DEBUG > 0:
        print(" next(%d/%d (all: %d)) --> %s"%(n+1,options.nprocess,len(stubs),stub))
        
    with open('%s/%s.out'%(options.base,stub),"r") as f:
        data_out = f.read()
    with open('%s/%s.err'%(options.base,stub),"r") as f:
        data_err = f.read()

    # analyze the logs
    if DEBUG > 1:
        print(f"Err:\n {data_err}")
        print(f"Out:\n {data_out}")
    
    config = ''
    version = ''
    dataset = ''
    file = ''
    status = -1                                    # did not find a proper ending or a known error
    stime = 0
    etime = 0
    n_lfn = -1
    n_output = -1

    for line in data_out.split('\n'):
        if options.debug > 1:
            print("LINE: ",line)

        if ' Arguments: ' in line:
            f = line.split('/')
            config = f[-4]
            version = f[-3]
            dataset = f[-2]
            file = f[-1].replace('.root','')
        elif ' start time    : ' in line:
            string = line.replace(' start time    : ','')
            if options.debug > 1:
                print(" STRING: %s"%(string))
            try:
                dt = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
                stime = int(dt.timestamp())
                #stime = int(time.mktime(time.strptime(string,PATTERN)))
            except:
                stime = int(time.mktime(time.strptime(string,PATTERN_B)))
        elif ' end   time    : ' in line:
            string = line.replace(' end   time    : ','')
            if options.debug > 1:
                print(" STRING: %s"%(string))
            try:
                dt = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
                etime = int(dt.timestamp())
                #etime = int(time.mktime(time.strptime(string,PATTERN)))
            except:
                etime = int(time.mktime(time.strptime(string,PATTERN_B)))
        elif ' download worked ' in line:
            status = 0

    # filter out unidentified files
    if config == "":
        return

    a = atom.Atom(config,version,dataset,file,status,stime,etime)
    key,value = a.summary()
    if key in record:
        print(" ERROR - tried to process this file twice.")
        saveFiles(options.base,stub,int(options.debug))
        return
    else:
        if a.status == -1:
            print("\n ==== FOUND UNKNOWN ERROR ====  Dumping files\n")
            print(" ==== OUTPUT ====\n%s"%data_out)
            print(" ==== ERROR ====\n%s"%data_err)
            a.show()
            print(' Out file: %s/%s.out'%(options.base,stub))
            print(' Err file: %s/%s.err'%(options.base,stub))
            saveFiles(options.base,stub,int(options.debug))
            return
        else:
            record[key] = value
            if options.debug > 0:
                a.show()

    # make sure not to process again
    moveFiles(options.base,stub,int(options.debug))

    return

def makeCompleteDir(dir):
    # make directory were files are moved once processed
    os.system("mkdir -p %s-done"%(dir))
    os.system("mkdir -p %s-save"%(dir))
    return

def moveFiles(dir,stub,debug):
    # make directory were files are moved once processed
    cmd = "mv %s/%s.??? %s-done/"%(dir,stub,dir)
    if debug > 1:
        print(" Moving: %s"%(cmd))
    os.system(cmd)
    return

def plot(record,min_t,max_t,opt='ALL',name='tmp'):

    nbins = 100
    if options.debug>1:
        print(" Plot request: range(%d,%d) nbins(%d) inputs(%d)"%(min_t,max_t,nbins,len(record)))
    
    # plot the record with the given option
    if opt == "save":
        #plt.text(0.01,0.99,name,ha='right',va='top')
        plt.legend(loc='upper left')
        plt.xlabel('date/time [%s]'%(name), fontsize=18)
        # save plot for later viewing
        plt.savefig(f"{TASK}_activity_{name}.png",bbox_inches='tight',dpi=400)
        plt.close()
    elif opt == "show":
        # show the plot for interactive use
        #plt.text(0.01,0.99,name,ha='right',va='top')
        plt.legend(loc='upper left')
        plt.show()
    else:
        times = []
        for key in record:
            f = record[key].split(':')
            status = f[0]
            etime = int(f[1])
            if opt == 'ALL' or opt == status:
                if etime >= min_t and etime <= max_t:
                    times.append(etime)
        if options.debug>1:
            print(" Total entries: ")

        npts = np.array(times)
        datetimes = [datetime.datetime.fromtimestamp(npt) for npt in npts]
        daterange = [datetime.datetime.fromtimestamp(npt) for npt in [min_t,max_t]]
                   
        # define the figure
        if opt == 'ALL':
            plt.figure(f" {TASK} Activity")
    
        if options.debug>1:
            print(" Plotting for option '%s'; n = %d"%(opt,len(times)))
        if len(times) < 1:
            return
        
        if opt == 'ALL':
            #min_t = min(times)
            #max_t = max(times)
            #mrange = mlp.dates.epoch2num([min_t,max_t])
            #print("SET Min: %d,  Max: %d"%(min_t,max_t))
            #plt.hist(times, 30, histtype='step', range=(min_t,max_t), linewidth=2.0, label=opt)
            plt.hist(datetimes, nbins, histtype='step', range=(daterange[0],daterange[1]), linewidth=1.0, label=opt)
            # make plot nicer
            plt.xlabel('date/time', fontsize=18)
            plt.ylabel('number of executions / interval', fontsize=18)
       
            # make axis tick numbers larger
            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)
            plt.xticks(rotation=45, ha='right')  # rotate x-axis labels for better readability
            plt.gca().xaxis.set_major_formatter(mlp.dates.DateFormatter('%m/%d %H:%M')) # format x-axis as date/time
        
            # make sure to noe have too much white space around the plot
            plt.subplots_adjust(top=0.99, right=0.99, bottom=0.23, left=0.18)
            
        else:
            #print("USE Min: %d,  Max: %d"%(min_t,max_t))
            #plt.hist(times), 30, histtype='step', range=(min_t,max_t), linewidth=2.0, label=opt)
            plt.hist(datetimes, nbins, histtype='step', range=(daterange[0],daterange[1]), linewidth=1.0, label=opt)

    return (min_t,max_t)
        
def plotRecord(record):
    # produce all standard plots for a given record
    
    print(" Plotting latest record (%d)"%(len(record)))

    # last recorded time (now)
    max_t = int(time.time())

    # last 2 hours
    min_t = max_t - (2 * 3600)

    plot(RECORD,min_t,max_t,'ALL')
    plot(RECORD,min_t,max_t,'0')
    plot(RECORD,min_t,max_t,'-1')
    plot(RECORD,min_t,max_t,'-2')
    plot(RECORD,min_t,max_t,'-3')
    plot(RECORD,min_t,max_t,'save','2hr')
    
    # last 4 hours
    min_t = max_t - (4 * 3600)
    plot(RECORD,min_t,max_t,'ALL')
    plot(RECORD,min_t,max_t,'0')
    plot(RECORD,min_t,max_t,'-1')
    plot(RECORD,min_t,max_t,'-2')
    plot(RECORD,min_t,max_t,'-3')
    plot(RECORD,min_t,max_t,'save','4hr')
    
    # last day
    min_t = max_t - (24 * 3600)
    plot(RECORD,min_t,max_t,'ALL')
    plot(RECORD,min_t,max_t,'0')
    plot(RECORD,min_t,max_t,'-1')
    plot(RECORD,min_t,max_t,'-2')
    plot(RECORD,min_t,max_t,'-3')
    plot(RECORD,min_t,max_t,'save','day')
    
    # last week
    min_t = max_t - (7 * 24 * 3600)
    plot(RECORD,min_t,max_t,'ALL')
    plot(RECORD,min_t,max_t,'0')
    plot(RECORD,min_t,max_t,'-1')
    plot(RECORD,min_t,max_t,'-2')
    plot(RECORD,min_t,max_t,'-3')
    plot(RECORD,min_t,max_t,'save','week')
    #plot(RECORD,min_t,max_t,'show')
        
    # last month
    min_t = max_t - (30 * 24 * 3600)
    plot(RECORD,min_t,max_t,'ALL')
    plot(RECORD,min_t,max_t,'0')
    plot(RECORD,min_t,max_t,'-1')
    plot(RECORD,min_t,max_t,'-2')
    plot(RECORD,min_t,max_t,'-3')
    plot(RECORD,min_t,max_t,'save','month')
    #plot(RECORD,min_t,max_t,'show','month')

def readRecord():
    # write the record efficicently to file

    record = {}
    filename = f"{options.base}/{TASK}Activity.db"
    
    if not os.path.exists(filename):
        print(" No previously existing record found.")
        return record
        
    print(" Reading record from existing file.")
    
    with open(f"{options.base}/{TASK}Activity.db","r") as f:
        data = f.read()
    for d in data.split("\n"):
        if ',' not in d:
            continue
        (key, value) = d.split(",")
        record[key] = value
    print(" record read (%d)."%(len(record)))
    return record

def saveFiles(dir,stub,debug):
    # make directory were files are moved once processed
    cmd = "mv %s/%s.??? %s-save/"%(dir,stub,dir)
    if debug > 1:
        print(" Moving: %s"%(cmd))
    os.system(cmd)
    return
        
def writeRecord(record):
    # write the record efficicently to file
    print(" Saving latest record (%d)."%(len(record)))
    with open(f"{options.base}/{TASK}Activity.db","w") as f:
        for key in record:
            f.write('%s,%s\n'%(key,record[key]))
    return

#---------------------------------------------------------------------------------------------------
#                                         M A I N
#---------------------------------------------------------------------------------------------------
# define and get all command line arguments
parser = OptionParser()
parser.add_option("-b","--base",dest="base",default='/home/tier3/cmsprod/cms/logs/fibs/download',help="base directory")
parser.add_option("-n","--nprocess",dest="nprocess",default=-1,help="number of files to process")
parser.add_option("-d","--debug",dest="debug",default=0,help="debug level")
(options, args) = parser.parse_args()

options.debug = int(options.debug)
options.nprocess = int(options.nprocess)

# make a spot to store processed files
makeCompleteDir(options.base)

# read the existing record
RECORD = readRecord()

# make sure there is a plot available before updating
plotRecord(RECORD)

# get the job file stubs to analyze
stubs = findAllJobStubs(options.base,int(options.debug))

# loop through the job stubs
n = 0
for stub in stubs:

    # review the record
    reviewStub(RECORD,options,stub)

    # make sure we can break out without processing everything
    if n+1 >= int(options.nprocess) and int(options.nprocess)>0:
        print(" EXIT - Reached maximum requested stubs.")
        break

    n += 1
    if n%100 == 0:           # save record every hundred files
        writeRecord(RECORD)
    if n%1000 == 0:          # plot most up to date status every 1000 files
        plotRecord(RECORD)

# Create most up to data record with plots
        
# write the results into the existing file
writeRecord(RECORD)

# plot present record
plotRecord(RECORD)
