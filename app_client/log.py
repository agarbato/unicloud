from time import sleep,strftime
from conf import *

class Log(object):
   filename = ""
   format="%Y/%m/%d %H:%M:%S"
   def __init__(self,logfile):
     self.logfile = logfile
     self.filename = open(logfile,"a")
   def header(self):
     self.filename.write("\n======================================================================================")
   def sync_start(self):
     self.filename.write("\n%s Unicloud Sync Started\n" % strftime(self.format))
   def sync_end(self,result):
     self.result = result
     self.filename.write("\n%s" % result[3])
     self.filename.write("\n%s Unicloud Sync %s, Pid %d, Exitcode %d" % (strftime(self.format), result[2], int(result[0]), int(result[1])))
   def client_error(self,result):
     self.result = result
     self.filename.write("\n%s %s" % ( strftime(self.format), result ))
     self.header()
     self.close()
   def close(self):
     self.filename.close()


