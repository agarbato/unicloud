import subprocess
import time

class ShellCmd(object):
    output={}
    child=[]
    rc=0
    pid=0
    def __init__(self,cmd):
      self***REMOVED***cmd  = cmd
      out = subprocess***REMOVED***Popen([cmd],
        shell=True,
        stdout=subprocess***REMOVED***PIPE,
        stderr=subprocess***REMOVED***STDOUT)
      stdout,stderr = out***REMOVED***communicate()
      self***REMOVED***output = stdout***REMOVED***decode()[:-1]
      self***REMOVED***rc=out***REMOVED***returncode
      self***REMOVED***pid=out***REMOVED***pid
      #print (self***REMOVED***output)
    def __repr__(self):
      return self***REMOVED***output
    def getrc(self):
      return self***REMOVED***rc
    def getpid(self):
      return self***REMOVED***pid

