from time import sleep, strftime
import logging
from logging.handlers import RotatingFileHandler
from conf import *


class Log(object):
   filename = ""
   format = "%Y/%m/%d %H:%M:%S"

   def __init__(self, logfile):
     self.logfile = logfile
     self.logger = logging.getLogger("Rotating Log")
     self.logger.setLevel(logging.INFO)
     self.handler = RotatingFileHandler(self.logfile, maxBytes=20971520, backupCount=5)
     self.logger.addHandler(self.handler)

   def header(self):
     self.logger.info("======================================================================================")

   def sync_start(self):
     self.header()
     self.logger.info(f"{strftime(self.format)} Unicloud Sync Started")

   def sync_end(self, result):
     self.result = result
     self.logger.info(f"{result[3]}")
     self.logger.info(f"{strftime(self.format)} Unicloud Sync {result[2]}, Pid {int(result[0])}, Exitcode {int(result[1])}")
     self.header()
     self.close()

   def client_error(self, result):
     self.result = result
     self.logger.info(f"{strftime(self.format)} {result}")
     self.header()
     self.close()

   def close(self):
      self.handler.close()
      self.logger.removeHandler(self.handler)


