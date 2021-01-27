from client_mgt import ClientMgt
from share_mgt import ShareMgt
from db_conn import get_db, query_db
from conf import *


def scheduler_tasks_update_sync_status(app):
    with app***REMOVED***app_context():
        cl = ClientMgt("all")
        client_list = cl***REMOVED***list_clients_threshold()
        if client_list:
            #print("Found some clients with a threshold defined***REMOVED******REMOVED***")
            for c in client_list:
                #print(c)
                c_status = ClientMgt(c[0])
                sync_status = c_status***REMOVED***sync_status(type='real_status')
                #print(sync_status)
                c_status***REMOVED***update_sync_status(sync_status)
        #else:
        #  print("No Client with threshold defined")
        #return client_list

def scheduler_tasks_share_update_size(app):
    with app***REMOVED***app_context():
      share = ShareMgt("all")
      share_list = share***REMOVED***share_list()
      if share_list:
          #print("Found some shares")
          for s in share_list:
              #print (s[0])
              s_size = ShareMgt(s[0])
              s_size***REMOVED***updatesize()
              #print(size)

def scheduler_tasks_purge_logs(app):
    with app***REMOVED***app_context():
        query = "select max(id) from events"
        maxid = query_db(query)
        if maxid[0][0] > int(max_log_events):
           query = "select max(id-%d) from events where log!=''" % int(max_log_events)
           #print(query)
           start_id_to_delete = query_db(query)
           query = "update events set log='None' where id < %d" % start_id_to_delete[0][0]
           #print(query)
           query_db(query)
           get_db()***REMOVED***commit()
           query = "vacuum"
           query_db(query)
           get_db()***REMOVED***commit()
        else:
           print("Not reached max log events yet : %d" % int(max_log_events))


#import sqlite3
#conn = sqlite3***REMOVED***connect('my_test***REMOVED***db', isolation_level=None)
#conn***REMOVED***execute("VACUUM")
#conn***REMOVED***close()