# dblock.py
import os
import socket
import MySQLdb

Db = MySQLdb.connect(read_default_file="/etc/my.cnf",read_default_group="mysql",db="Fibs")
Cursor = Db.cursor()

class dblock(object):
    '''Class to handle creating and removing database based locks'''

    # custom exceptions
    class DatabaseLockAcquisitionError(Exception):
        pass
    class DatabaseLockReleaseError(Exception):
        pass

    # convenience callables for formatting
    addr = lambda self: '%d@%s' % (self.pid, self.host)
    fddr = lambda self: '<%s %s>' % (self.path, self.addr())
    pddr = lambda self, lock: '<%s %s@%s>' %\
                              (self.path, lock['pid'], lock['host'])

    def __init__(self,path,debug=None):
        self.pid   = os.getpid()
        self.host  = socket.gethostname()
        self.path  = path
        self.debug = debug                                       # set this to get status messages
        self.acquireSql = "insert into Locks(LockPath,LockHost,LockPid) " \
            + " values('%s','%s',%d);"%(self.path,self.host,self.pid)
        self.releaseSql = "delete from Locks where LockPath='%s'"%(self.path)
        self.listSql = "select * from Locks where LockPath='%s';"%(self.path)

    def acquire(self):
        '''Acquire a lock, returning self if successful, False otherwise'''

        try:
            # Execute the SQL command
            Cursor.execute(self.acquireSql)
            if self.debug:
                print 'Acquired lock: %s' % self.fddr()
        except:
            if self.debug:
                lock = self._readlock()
                print 'Existing lock detected: %s' % self.pddr(lock)
            return False

        return self

    def release(self):
        '''Release lock, returning self'''

        if self.ownlock():
            try:
                # Execute the SQL command
                Cursor.execute(self.releaseSql)
                if self.debug:
                    print 'Released lock: %s' % self.fddr()
            except:
                print " Error (%s): unable to release lock."%(self.releaseSql)
                raise (self.DatabaseLockReleaseError,
                       'Error releasing lock: %s' % self.fddr())
        return self


    def _readlock(self):
        '''Internal method to read lock info'''

        lock = {}
        try:
            Cursor.execute(self.listSql)
            results = Cursor.fetchall()
            if   len(results) == 0:
                lock['path'], lock['host'], lock['pid'] = [ self.path, '', 0 ]                
            elif len(results) > 1:
                print ' WARNING -- did not find unique result! (n=%d)'%(len(results)) 
                lock['path'], lock['host'], lock['pid'] = [ self.path, '', 0 ]
            else:
                for row in results:
                    lock['path'], lock['host'], lock['pid'] = row
        except:
            print " Error (%s): unable to list locks."%(self.listSql)
            lock['path'], lock['host'], lock['pid'] = [ self.path, '', 0 ]

        return lock

    def ownlock(self):
        '''Check if we own the lock'''
        lock = self._readlock()
        return (self.fddr() == self.pddr(lock))

    def __del__(self):
        '''Magic method to clean up lock when program exits'''
        self.release()
