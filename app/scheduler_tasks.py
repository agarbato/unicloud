import time
import json
import os
from homestats import *
from client_mgt import ClientMgt
from share_mgt import ShareMgt
from db_conn import get_db, query_db
from requests import post
from time import strftime
from conf import *

time_format = "[%Y:%m:%d %H:%M:%S]"


def scheduler_tasks_update_sync_status(app):
    print(f"{strftime(time_format)} - Scheduled task: Update Client Sync status on DB")
    with app.app_context():
        cl = ClientMgt("all")
        client_list = cl.list_clients_threshold()
        if client_list:
            for c in client_list:
                c_status = ClientMgt(c[0])
                sync_status = c_status.sync_status(type='real_status')
                c_status.update_sync_status(sync_status)


def scheduler_tasks_home_assistant_post(sensor_name, data):
    url = f"{home_assistant_url}/api/states/sensor.unicloud_{sensor_name}"
    headers = {
        'Authorization': f'Bearer {home_assistant_token}',
        'content-type': 'application/json',
    }
    post(url, headers=headers, data=json.dumps(data))


def scheduler_tasks_update_home_assistant_server(app, startTime):
    print(f"{strftime(time_format)} - Scheduled task: Update Home Assistant Server stats")
    with app.app_context():
        unicloud_stats = homestats_unicloud()
        runtime_stats = homestats_runtime()
        sys_stats = homestats_sys(startTime)
        sensor_name = "server"
        data = {"state": f"Uptime {sys_stats['uptime_days']}d, {sys_stats['uptime_hours']}h, "
                         f"{sys_stats['uptime_minutes']}m, {sys_stats['uptime_seconds']}s",
                "attributes": {"Total Events": unicloud_stats['nevents'], "OK Events": unicloud_stats['nevents_ok'],
                               "KO Events": unicloud_stats['nevents_ko'], "Number of Shares": unicloud_stats['nshares'],
                               "Clients Total": unicloud_stats['nclients'], "Clients to Register": unicloud_stats['toregister'],
                               "Clients Out of Sync:": unicloud_stats['outsync'], "Python_Version": runtime_stats['python_version'],
                               "Unison Version": runtime_stats['unison_version'], "Flask Version": runtime_stats['flask_version']}}
        scheduler_tasks_home_assistant_post(sensor_name, data)


def scheduler_tasks_update_home_assistant_clients(app):
    print(f"{strftime(time_format)} - Scheduled task: Update Home Assistant Clients stats")
    with app.app_context():
        cl = ClientMgt("all")
        client_list = cl.list_clients()
        for c in client_list:
            sensor_name = f"client_{c[0].replace('-', '_')}"
            c_data = ClientMgt(c[0])
            sync_status = c_data.sync_status(type='real_status')
            client_info = c_data.info()
            lastseen = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(client_info['lastseen']))
            data = {f"state": sync_status,
                    "attributes": {"Share": client_info['share'], "Last_Seen": lastseen,
                                   "average_sync_duration": client_info['avg_duration'],
                                   "Sync_Ok": client_info['ok'], "Sync_Ko": client_info['ko'],
                                   "Sync_Threshold": client_info['threshold'], "Sync_Total": client_info['total']}}
            scheduler_tasks_home_assistant_post(sensor_name, data)


def scheduler_tasks_update_home_assistant_shares(app):
    print(f"{strftime(time_format)} - Scheduled task: Update Home Assistant Share stats")
    with app.app_context():
        sh = ShareMgt("all")
        share_list = sh.share_list()
        for s in share_list:
            sensor_name = f"share_{s[0].replace('-', '_')}"
            s_data = ShareMgt(s[0])
            share_info = s_data.info("all")
            data = {f"state": share_info['size'],
                    "attributes": {"Description": share_info['description'], "Clients": share_info['clients'],
                                   "Clients_Count": share_info['clients_count']}}
            scheduler_tasks_home_assistant_post(sensor_name, data)


def scheduler_tasks_share_update_size(app):
    print(f"{strftime(time_format)} - Scheduled task: Update Shares size on db")
    with app.app_context():
        share = ShareMgt("all")
        share_list = share.share_list()
        if share_list:
            for s in share_list:
                s_size = ShareMgt(s[0])
                s_size.updatesize()


def scheduler_tasks_purge_logs(app):
    print(f"{strftime(time_format)} - Scheduled task: Purge Logs")
    with app.app_context():
        query = "select max(id) from events"
        maxid = query_db(query)
        if maxid[0][0] > int(max_log_events):
            query = "select max(id-%d) from events where log!=''" % int(max_log_events)
            start_id_to_delete = query_db(query)
            query = "update events set log='None' where id < %d" % start_id_to_delete[0][0]
            query_db(query)
            get_db().commit()
            query = "vacuum"
            query_db(query)
            get_db().commit()
        else:
            print("Not reached max log events yet : %d" % int(max_log_events))


def scheduler_tasks_remove_locks(directory):
    print(f"{strftime(time_format)} - Scheduled task: Remove Lock files")
    now = time.time()
    olderthreshold = 7200
    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.startswith("lk")]
    for file in filtered_files:
        filestamp = os.stat(os.path.join(directory, file)).st_mtime
        filecompare = now - olderthreshold
        if filestamp < filecompare:
            os.remove(f"{directory}/{file}")
