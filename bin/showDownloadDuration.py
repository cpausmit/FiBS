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

TASK = 'download'
DEBUG = 0

def plotDurationVsStart(data, name, xtitle, ytitle):
    xs = []
    ys = []
    for key in data:
        status,start,end = data[key].split(':')
        duration = int(end) - int(start)
        if int(status) == 0:
            xs.append(int(start))
            ys.append(duration)

    # define the figure
    plt.figure(name)
    #plt.plot(xs,ys,marker="o",ls='dashed')
    #plt.scatter(xs,ys,marker="o")
    x_, y_ = np.meshgrid(xs,ys)
    plt.contourf(x_,y_)
    
    # make plot nicer
    plt.xlabel(xtitle, fontsize=18)
    plt.ylabel(ytitle, fontsize=18)
    
    # make axis tick numbers larger
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    
    # make sure to noe have too much white space around the plot
    plt.subplots_adjust(top=0.99, right=0.99, bottom=0.13, left=0.12)
    
    # save plot for later viewing
    plt.savefig(name+".png",bbox_inches='tight',dpi=400)
    
    # show the plot for interactive use
    plt.ylim(0)
    #plt.yscale("log")
    plt.show()

    

def plotDuration(data, name, xtitle, ytitle):

    xs = []
    xes = []
    for key in data:
        status,start,end = data[key].split(':')
        duration = int(end) - int(start)
        if int(status) == 0:
            xs.append(duration)
        else:
            print(" Error")
            xes.append(duration)


    # define the figure
    plt.figure(name)
    n, bins, patches = plt.hist(xs, 200, histtype='step', linewidth=2.0)
    n, bins, patches = plt.hist(xes, 200, histtype='step', linewidth=2.0)
    
    # make plot nicer
    plt.xlabel(xtitle, fontsize=18)
    plt.ylabel(ytitle, fontsize=18)
    
    # make axis tick numbers larger
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    
    # make sure to noe have too much white space around the plot
    plt.subplots_adjust(top=0.99, right=0.99, bottom=0.13, left=0.12)
    
    # save plot for later viewing
    plt.savefig(name+".png",bbox_inches='tight',dpi=400)
    
    # show the plot for interactive use
    plt.xlim(0)
    plt.yscale("log")
    plt.show()
    
    
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

#---------------------------------------------------------------------------------------------------
#                                         M A I N
#---------------------------------------------------------------------------------------------------
# define and get all command line arguments
parser = OptionParser()
parser.add_option("-b","--base",dest="base",default='/home/tier3/cmsprod/cms/logs/fibs/download',help="base directory")
parser.add_option("-d","--debug",dest="debug",default=0,help="debug level")
(options, args) = parser.parse_args()

options.debug = int(options.debug)

# read the existing record
RECORD = readRecord()

# make sure there is a plot available before updating
plotDuration(RECORD,'duration','download duration [s]','number or downloads')
plotDurationVsStart(RECORD,'duration vs start','download start','download duration [s]')
