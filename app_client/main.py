import time
import requests
import os
from conf import *
from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime
from shell import ShellCmd
from log import Log

root_dir = "/data"
log_dir = f"{root_dir}/log"
logfile = f"{log_dir}/client.log"
logfile_auth_keys = f"{log_dir}/sync_auth_keys.log"
logfile_replica = f"{log_dir}/replica_server.log"
lockfile = f"{log_dir}/client.lock"
command = "unison unicloud"

start_sync_url = f"{server_api_protocol}://{server_api_hostname}:{server_api_port}/sync/start/{client_hostname}"
end_sync_url = f"{server_api_protocol}://{server_api_hostname}:{server_api_port}/sync/end/{client_hostname}"
share_exist_url = f"{server_api_protocol}://{server_api_hostname}:{server_api_port}/shares/exist"


def get_ts():
  ts = int(time.time())
  return ts


def start_sync(log, start_ts):
  #result[0]pid result[1]rc result[2]status result[3]log result[4]sync_status
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
      unisonstderr = run.rstderr()
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


def remove_lock(directory):
  files_in_directory = os.listdir(directory)
  filtered_files = [file for file in files_in_directory if file.startswith("lk")]
  for file in filtered_files:
    os.remove(f"{directory}/{file}")


def scheduler_sync():
  remove_lock(f"{root_dir}/.unison")
  log = Log(logfile)
  start_ts = get_ts()
  result = start_sync(log, start_ts)
  #print (result)
  if result == 6 or result == 503:
    log.client_error(f"Client {client_hostname} can't contact API Server [ {start_sync_url} ]")
  elif result == 500:
    log.client_error(f"Client {client_hostname} is not enabled, enable it from server UI")
  else:
    end_sync(result, start_ts, log)
  log.close()


def sync_auth_keys():
  log = Log(logfile_auth_keys)
  log.ssh_keys_sync_start()
  command = "unison unicloud_replica_ssh_keys"
  run = ShellCmd(command)
  if run.getrc() == 0:
    result = "OK"
  else:
    result = "KO"
  log.ssh_keys_sync_end(result)


# THE SCHEDULER


scheduler = BlockingScheduler({
  'apscheduler.jobstores.default': {
    'type': 'sqlalchemy',
    'url': f'sqlite:////{root_dir}/jobs.sqlite'
  }
})

scheduler.add_job(func=scheduler_sync, id="unison_sync_job", trigger="interval", seconds=int(sync_interval), next_run_time=datetime.now(), replace_existing=True)
if role == "replica_server":
  scheduler.add_job(func=sync_auth_keys, id="unison_sync_auth_key", trigger="interval", seconds=60, next_run_time=datetime.now(), replace_existing=True)
scheduler.start()




