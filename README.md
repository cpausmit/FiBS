# FiBS - A Light Weight Fi(le) B(atch) S(ystem)

FiBS is very simple batch system which uses a locking mechanism as batch manager and engines that freely request a lock to pull there work of a list which is stored in a file. The task the batch manager executes has a configuration file and an initialization file and will be excuted using the entries in the provided list.

This system is extremely simple but of course has many limitations. It is ideal to execute a large number of parallel tasks that do not require a lot of resources and can run in parallel on machines that are busy with more heavy computing. Transfering files is an ideal task for FiBS.

## Installation

To download the software use git clone:

    git clone https://github.com/cpausmit/FiBS

install pdsh as root

	yum install pdsh

## Running a simple task: fake

Set BASE of setup.sh as the pwd and source it

	source ./setup.sh

Make sure all necessary files are downloaded

Make directories named logs, work, and $FIBS+WORK $FIBS_LOGS 

	mkdir ~/logs 
	mkdir ~/work
	mkdir -p $FIBS+WORK $FIBS_LOGS

Make an executable task, and a configure executable. In the task write what you want to do with the task, and with the configure executable for the task write a task name (it should be the same as the task executable name) make a list for the task to run, make the nuber of entries that the task completes at a time, write a error code, then write a list of workers to execute the task, and then assign the number of processes the workers take in. this is an example of the configurement of a task named fake:
 
	[general]
	task = fake.py
	list = fake.list
	nentries = 2

	[io]
	outerr = fake

	[workers]
	list = T3BTCH001.MIT.EDU T3BTCH002.MIT.EDU T3BTCH003.MIT.EDU
	nprocesses = 2

once everything is written run the task

## Sub directories

### ./bin

A sub-directory full of executables to preform services relating to FiBS

### ./config

A sub-directory with executabels to make, upload, and check files

### ./python

A sub-directory with code for running python scripts for tasks
