import time
import json
from homestats import *
from client_mgt import ClientMgt
from share_mgt import ShareMgt
from db_conn import get_db, query_db
from requests import post
from conf import *


def scheduler_tasks_update_sync_status(app):
    with app***REMOVED***app_context():
        cl = ClientMgt("all")
        client_list = cl***REMOVED***list_clients_threshold()
        if client_list:
            # print("Found some clients with a threshold defined***REMOVED******REMOVED***")
            for c in client_list:
                # print(c)
                c_status = ClientMgt(c[0])
                sync_status = c_status***REMOVED***sync_status(type='real_status')
                # print(sync_status)
                c_status***REMOVED***update_sync_status(sync_status)
        # else:
        #  print("No Client with threshold defined")
        # return client_list


def scheduler_tasks_home_assistant_post(sensor_name, data):
    url = f"{home_assistant_url}/api/states/sensor***REMOVED***unicloud_{sensor_name}"
    headers = {
        'Authorization': f'Bearer {home_assistant_token}',
        'content-type': 'application/json',
    }
    post(url, headers=headers, data=json***REMOVED***dumps(data))


def scheduler_tasks_update_home_assistant_server(app, startTime):
    with app***REMOVED***app_context():
        print("Sever stats")
        unicloud_stats = homestats_unicloud()
        runtime_stats = homestats_runtime()
        sys_stats = homestats_sys(startTime)
        sensor_name = "server"
        data = {"state": f"Uptime {sys_stats['boot_uptime_days']}d, {sys_stats['boot_uptime_hours']}h, "
                         f"{sys_stats['boot_uptime_minutes']}m, {sys_stats['boot_uptime_seconds']}s",
                "attributes": {"Total Events": unicloud_stats['nevents'], "OK Events": unicloud_stats['nevents_ok'],
                               "KO Events": unicloud_stats['nevents_ko'], "Number of Shares": unicloud_stats['nshares'],
                               "Clients Total": unicloud_stats['nclients'], "Clients to Register": unicloud_stats['toregister'],
                               "Clients Out of Sync:": unicloud_stats['outsync'], "Python_Version": runtime_stats['python_version'],
                               "Unison Version": runtime_stats['unison_version'], "Flask Version": runtime_stats['flask_version']}}
        print(data)
        scheduler_tasks_home_assistant_post(sensor_name, data)

#result***REMOVED***update({'python_version': python_version, 'unison_version': unison_version, 'flask_version': flask_version })
#result***REMOVED***update({'nevents': nevents[0][0], 'nevents_ok': nevents_ok[0][0], 'nevents_ko': nevents_ko[0][0], 'thresholds': thresholds[0][0],
#            'nclients': nclients[0][0], 'nshares': nshares[0][0], 'toregister': toregister[0][0], 'outsync': outsync[0][0], 'active': active[0][0]})
# for f in uptime_days, uptime_hours, uptime_minutes, uptime_seconds:


def scheduler_tasks_update_home_assistant_clients(app):
    with app***REMOVED***app_context():
        cl = ClientMgt("all")
        client_list = cl***REMOVED***list_clients()
        for c in client_list:
            sensor_name = f"client_{c[0]***REMOVED***replace('-', '_')}"
            c_data = ClientMgt(c[0])
            sync_status = c_data***REMOVED***sync_status(type='real_status')
            client_info = c_data***REMOVED***info()
            lastseen = time***REMOVED***strftime("%Y-%m-%d %H:%M:%S", time***REMOVED***localtime(client_info['lastseen']))
            data = {f"state": sync_status,
                    "attributes": {"Share": client_info['share'], "Last_Seen": lastseen,
                                   "average_sync_duration": client_info['avg_duration'],
                                   "Sync_Ok": client_info['ok'], "Sync_Ko": client_info['ko'],
                                   "Sync_Threshold": client_info['threshold'], "Sync_Total": client_info['total']}}
            # print(data)
            scheduler_tasks_home_assistant_post(sensor_name, data)


def scheduler_tasks_update_home_assistant_shares(app):
    print("share task")
    with app***REMOVED***app_context():
        sh = ShareMgt("all")
        share_list = sh***REMOVED***share_list()
        for s in share_list:
            sensor_name = f"share_{s[0]***REMOVED***replace('-', '_')}"
            s_data = ShareMgt(s[0])
            share_info = s_data***REMOVED***info("all")
            print(share_info['size'])
            data = {f"state": share_info['size'],
                    "attributes": {"Description": share_info['description'], "Clients": share_info['clients'],
                                   "Clients_Count": share_info['clients_count']}}
            # print(data)
            scheduler_tasks_home_assistant_post(sensor_name, data)



def scheduler_tasks_share_update_size(app):
    with app***REMOVED***app_context():
        share = ShareMgt("all")
        share_list = share***REMOVED***share_list()
        if share_list:
            # print("Found some shares")
            for s in share_list:
                # print (s[0])
                s_size = ShareMgt(s[0])
                s_size***REMOVED***updatesize()
                # print(size)


# result***REMOVED***update({'name': q[0][0], 'path': q[0][1], 'description': q[0][2], 'size': q[0][3], 'clients': client_list_final, 'clients_count': q3[0][0] })


def scheduler_tasks_purge_logs(app):
    with app***REMOVED***app_context():
        query = "select max(id) from events"
        maxid = query_db(query)
        if maxid[0][0] > int(max_log_events):
            query = "select max(id-%d) from events where log!=''" % int(max_log_events)
            # print(query)
            start_id_to_delete = query_db(query)
            query = "update events set log='None' where id < %d" % start_id_to_delete[0][0]
            # print(query)
            query_db(query)
            get_db()***REMOVED***commit()
            query = "vacuum"
            query_db(query)
            get_db()***REMOVED***commit()
        else:
            print("Not reached max log events yet : %d" % int(max_log_events))

# import sqlite3
# conn = sqlite3***REMOVED***connect('my_test***REMOVED***db', isolation_level=None)
# conn***REMOVED***execute("VACUUM")
# conn***REMOVED***close()
