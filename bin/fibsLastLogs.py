#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Script to find the youngest logfiles of completed jobs for a given FiBS task.
#---------------------------------------------------------------------------------------------------
import os,sys
import rex

def getJobsFromOutput(out):
    # decode the full find output and make a list of non zero err or out tasks

    jobSizes = {}

    for line in out.split('\n'):
        line = line[:-1]
        f = line.split(' ')
        if len(f) >= 3:
            size = f[1]
            job = f[2]
            job = ".".join(job.split(".")[:-1])
            job = job.replace("./","")
            if job in jobSizes:
                if jobSizes[job] < size:
                    jobSizes[job] = size
            else:
                jobSizes[job] = size
            #print ' job: %s'%(job)
    
    return jobSizes

# get our parameters as needed
base = os.environ.get('FIBS_BASE','')
logs = os.environ.get('FIBS_LOGS','')
minutes = "30"

if base == '':
    print ' ERROR - FIBS_BASE is not defined. EXIT '

if len(sys.argv) < 2:
    print ' ERROR - please specify task '
task = sys.argv[1]

if len(sys.argv) > 2:
    minutes = sys.argv[2]

os.chdir(logs+'/'+task);
cmd = "find ./ -cmin -" + minutes + " -printf \"%T@ %s %p\n\" | egrep \(.out\|.err\) | sort -n | tail -100"
rex = rex.Rex('none','none')
(rc,out,err) = rex.executeLocalAction(cmd)

# now print them out
jobSizes = getJobsFromOutput(out)

for job in jobSizes:
    size = jobSizes[job]
    if size > 1:
        print " %s/%s/%s.{err,out}"%(logs,task,job)
