from time import sleep,strftime
from conf import *

class Log(object):
   filename = ""
   format="%Y/%m/%d %H:%M:%S"
   def __init__(self,logfile):
     self***REMOVED***logfile = logfile
     self***REMOVED***filename = open(logfile,"a")
   def header(self):
     self***REMOVED***filename***REMOVED***write("\n======================================================================================")
   def sync_start(self):
     self***REMOVED***filename***REMOVED***write("\n%s Unicloud Sync Started\n" % strftime(self***REMOVED***format))
   def sync_end(self,result):
     self***REMOVED***result = result
     self***REMOVED***filename***REMOVED***write("\n%s" % result[3])
     self***REMOVED***filename***REMOVED***write("\n%s Unicloud Sync %s, Pid %d, Exitcode %d" % (strftime(self***REMOVED***format), result[2], int(result[0]), int(result[1])))
   def client_error(self,result):
     self***REMOVED***result = result
     self***REMOVED***filename***REMOVED***write("\n%s %s" % ( strftime(self***REMOVED***format), result ))
     self***REMOVED***header()
     self***REMOVED***close()
   def close(self):
     self***REMOVED***filename***REMOVED***close()


