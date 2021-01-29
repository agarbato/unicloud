import time
import requests
import os
#from time import sleep, strftime
from conf import *
from apscheduler.schedulers.background import BlockingScheduler
from shell import ShellCmd
from log import Log

root_dir = "/data"
log_dir = root_dir + "/log"
logfile = log_dir + "/client.log"
lockfile = log_dir + "/client.lock"
command = "unison unicloud"

start_sync_url = server_api_protocol + "://" +  server_hostname + ":" + server_api_port + "/sync/start/" + client_hostname
end_sync_url = server_api_protocol + "://" +  server_hostname + ":" + server_api_port + "/sync/end/" + client_hostname
share_exist_url = server_api_protocol + "://" +  server_hostname + ":" + server_api_port + "/shares/exist"


def get_ts():
  ts = int(time.time())
  return ts


def start_sync(log, start_ts):
  #result[0]pid result[1]rc result[2]status result[3]log result[4]sync_status
  log.header()
  log.sync_start()
  result = []
  #match = ['BGN', 'END', 'Nothing', 'Complete']
  data = {'share': server_share, 'start_ts': start_ts}
  try:
    r = requests.post(url=start_sync_url, data=data)
  except requests.ConnectionError:
    return 6
  else:
    if r.status_code == 200:
      run = ShellCmd(command)
      result.insert(0, run.getpid())
      result.insert(1, run.getrc())
      #print (run)
      if run.getrc() == 0:
        result.insert(2, 'OK')
      elif run.getrc() == 1 or run.getrc() == 2:
        result.insert(2, 'WARNING')
      else:
        result.insert(2, 'KO')
      unisonstderr=run.rstderr()
      result.insert(3, unisonstderr)
      if "Nothing to do" in unisonstderr:
        result.insert(4, "UNCHANGED")
      elif "Synchronization complete" in unisonstderr:
        result.insert(4, "CHANGED")
      elif "Synchronization incomplete" in unisonstderr:
        result.insert(4, "WARNING")
      else:
        result.insert(4, "UNKNOWN")
    else:
      result.insert(0, 0)
      result.insert(1, 0)
      result.insert(2, "ERROR")
      result.insert(3, "Connection Error")
      result.insert(4, "UNKNOWN")
  return result


def end_sync(result, start_ts, log):
  data = {'share': server_share, 'start_ts': start_ts, 'end_ts': int(time.time()), 'status': result[2], 'log': result[3], 'sync_status': result[4] }
  requests.post(url=end_sync_url, data=data)
  #log.client_error("Log received : %s" % result[3])
  log.sync_end(result)
  log.header()

def scheduler_sync():
  log = Log(logfile)
  start_ts = get_ts()
  result = start_sync(log, start_ts)
  #print (result)
  if result == 6 or result == 503:
    log.client_error("Client %s can't contact API Server [ %s ]" % (client_hostname, start_sync_url) )
  elif result == 500:
    log.client_error("Client %s is not enabled, enable it from server UI" % client_hostname)
  else:
    end_sync(result, start_ts, log)
  log.close()

# THE SCHEDULER

scheduler = BlockingScheduler()
scheduler.add_job(func=scheduler_sync, trigger="interval", seconds=int(sync_interval))
scheduler.start()

# THE WHILE LOOP

# while True:
#   if not os.path.exists(lockfile):
#     log = Log(logfile)
#     filevar = start_lock(lockfile)
#     start_ts = get_ts()
#     result = start_sync(log)
#     #print (result)
#     if result == 6 or result == 503:
#       log.client_error("Client %s can't contact API Server [ %s ]" % (client_hostname, start_sync_url) )
#     elif result == 500:
#       log.client_error("Client %s is not enabled, enable it from server UI" % client_hostname)
#     else:
#       end_sync(result, log)
#     remove_lock(lockfile, filevar)
#   else:
#     print ("Lock File exist, wait")
#   log.close()
#   sleep(int(sync_interval))



