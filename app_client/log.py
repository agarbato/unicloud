from time import sleep, strftime
from conf import *


class Log(object):
   filename = ""
   format = "%Y/%m/%d %H:%M:%S"

   def __init__(self, logfile):
     self.logfile = logfile
     self.filename = open(logfile, "a")

   def header(self):
     self.filename.write("\n======================================================================================")

   def sync_start(self):
     self.filename.write(f"\n{strftime(self.format)} Unicloud Sync Started\n")

   def sync_end(self, result):
     self.result = result
     self.filename.write(f"\n{result[3]}")
     self.filename.write(f"\n{strftime(self.format)} Unicloud Sync {result[2]}, Pid {int(result[0])}, Exitcode {int(result[1])}")

   def client_error(self, result):
     self.result = result
     self.filename.write(f"\n{strftime(self.format)} {result}")
     self.header()
     self.close()

   def close(self):
     self.filename.close()


