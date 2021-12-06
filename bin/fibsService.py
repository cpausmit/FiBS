#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# FiBS services.
#
#---------------------------------------------------------------------------------------------------
import os,sys,re
import ConfigParser

#===================================================================================================
#  H E L P E R S
#===================================================================================================
def testLocalSetup(debug=0):
    # The local setup needs a number of things to be present. Make sure all is there, or complain.

    # See whether we are setup
    base = os.environ.get('FIBS_BASE')
    if base=='':
        print '\n ERROR -- FiBS is not setup FIBS_BASE environment not set. EXIT!\n'
        sys.exit(1)

    return

#===================================================================================================
#  M A I N
#===================================================================================================
usage = " fibsService.py [status|start|stop] <task>\n"
if len(sys.argv) != 3:
    print "\n ERROR: input parameters.\n\n" + usage
    sys.exit(1)

service = sys.argv[1]
task = sys.argv[2]
configFile = os.environ.get('FIBS_CFGS') + '/' + task + '.cfg' 

print ' Config: ' + configFile

# reading detailed configurations
#--------------------------------
config = ConfigParser.RawConfigParser()
config.read(configFile)

# get our worker list
list = re.sub(' +',' ',config.get('workers','list'))
workers = list.split(" ")
workers_list = ','.join(workers)

script = ""
if   service == 'start':
    cmd = "voms-proxy-init --valid 168:00 -voms cms >& /dev/null"
    #print " CMD: " + cmd
    os.system(cmd)
    script = 'fibsStartRemoteOn'
    script_local = 'fibsStart'
elif service == 'stop':
    script = 'fibsStopRemoteOn'
    script_local = 'fibsStop'
elif service == 'status':
    script = 'fibsStatusRemoteOn'
    script_local = 'fibsStatus'
else:
    print '\n ERROR - service command not known: %s\n\n%s'%(service,usage)
    sys.exit(1)

# parallel processing
cmd = "pdsh -w %s %s %s | sort"%(workers_list,script_local,task)
rc = os.system(cmd)

# go one-by-one in case of failure
if rc != 0:
    for worker in workers:
        cmd = script + ' ' + worker + ' ' + task
        os.system(cmd)
