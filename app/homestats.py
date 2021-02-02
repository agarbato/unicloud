import os
import psutil
import subprocess
import flask
import sys
import time
from db_conn import get_db, query_db


def homestats_sys(startTime):
    result={}
    av1, av2, av3 = os.getloadavg()
    av1 = round(av1, 2)
    av2 = round(av2, 2)
    av3 = round(av3, 2)
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    bootDelta = int(time.time() - psutil.boot_time())
    processDelta = int(time.time() - startTime)
    boot_uptime = homestats_uptime(bootDelta)
    process_uptime = homestats_uptime(processDelta)
    result.update({'av1': av1, 'av2': av2, 'av3': av3, 'cpu_percent': cpu_percent, 'memory_percent': memory_percent,
                   'uptime_days': process_uptime[0], 'uptime_hours': process_uptime[1], 'uptime_minutes': process_uptime[2], 'uptime_seconds': process_uptime[3],
                   'boot_uptime_days': boot_uptime[0], 'boot_uptime_hours': boot_uptime[1], 'boot_uptime_minutes': boot_uptime[2], 'boot_uptime_seconds': boot_uptime[3]
                   })
    return result

def homestats_unicloud():
    result = {}
    query = "select count(id) from events"
    nevents = query_db(query)
    query = "select count(id) from events where status='OK'"
    nevents_ok = query_db(query)
    query = "select count(id) from events where status='KO'"
    nevents_ko = query_db(query)
    query = "select count(id) from clients"
    nclients = query_db(query)
    query = "select count(id) from shares"
    nshares = query_db(query)
    query = "select count(id) from clients where status='Registered'"
    toregister = query_db(query)
    query = "select count(id) from clients where status='Active'"
    active = query_db(query)
    query = "select count(id) from clients where sync_status='Out of Sync'"
    outsync = query_db(query)
    query = "select count(id) from clients where threshold!=0"
    thresholds = query_db(query)
    result.update({'nevents': nevents[0][0], 'nevents_ok': nevents_ok[0][0], 'nevents_ko': nevents_ko[0][0], 'thresholds': thresholds[0][0],
                  'nclients': nclients[0][0], 'nshares': nshares[0][0], 'toregister': toregister[0][0], 'outsync': outsync[0][0], 'active': active[0][0]})
    return result

def homestats_runtime():
    result = {}
    python_version = str(sys.version_info.major)+'.'+str(sys.version_info.minor)
    unison_version = subprocess.check_output(['unison', '-version']).split()[2].decode('utf-8')
    flask_version = flask.__version__
    result.update({'python_version': python_version, 'unison_version': unison_version, 'flask_version': flask_version })
    return result

def homestats_uptime(seconds):
    result = []
    #uptime_seconds=int(time.time() - seconds)
    uptime_days = int(seconds / 60 / 60 / 24 % 365)
    uptime_hours = int(seconds / 60 / 60 % 24)
    uptime_minutes = int(seconds / 60 % 60)
    uptime_seconds = int(seconds % 60)
    for f in uptime_days, uptime_hours, uptime_minutes, uptime_seconds:
        result.append(f)
    return result

