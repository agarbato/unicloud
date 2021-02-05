from db_conn import get_db, query_db

class Event(object):
    eventid = ""

    def __init__(self, eventid):
        self***REMOVED***eventid = int(eventid)

    def exist(self):
        query = "select count(id) from events where id=%d and status is not 'SYNCING'" % self***REMOVED***eventid
        if query_db(query)[0][0] > 0:
            return True
        else:
            return False

    def info(self):
        query = "select id,client,status,log,start_ts,end_ts,duration,share from events where id=%d" % self***REMOVED***eventid
        res = query_db(query)
        return res


def event_form(client, status, sync_status, limit=50):
    # ALL RESULTS
    if client == "ALL" and status == "ALL" and sync_status== "ALL" or client is None and status is None and sync_status is None: # ALL RESULTS
        query = "select client, start_ts, end_ts, status, duration, share, id, sync_status from events order by start_ts desc limit %d" % int(limit)
    # SPECIFIC CLIENT AND ALL STATUS AND ALL SYNC_STATUS
    elif client != "ALL" and status == "ALL" and sync_status == "ALL":
        query = "select client, start_ts, end_ts, status, duration, share, id, sync_status from events where client = '%s' order by start_ts desc limit %d" % (client,int(limit))
    # SPECIFIC CLIENT AND SPECIFIC STATUS AND ALL SYNC_STATUS
    elif client != "ALL" and status != "ALL" and sync_status == "ALL":
        query = "select client, start_ts, end_ts, status, duration, share, id, sync_status from events where client = '%s' and status = '%s' order by start_ts desc limit %d" % (client, status, int(limit))
    # SPECIFIC CLIENT AND SPECIFIC SYNC_STATUS AND ALL STATUS
    elif client != "ALL" and sync_status != "ALL" and status == "ALL":
        query = "select client, start_ts, end_ts, status, duration, share, id, sync_status from events where client = '%s' and sync_status = '%s' order by start_ts desc limit %d" % (client, sync_status, int(limit))
    # SPECIFIC CLIENT AND SPECIFIC STATUS AND SPECIFIC SYNC_STATUS
    elif client != "ALL" and status != "ALL" and sync_status != "ALL":
        query = "select client, start_ts, end_ts, status, duration, share, id, sync_status from events where client = '%s' and status = '%s' and sync_status = '%s' order by start_ts desc limit %d" % (client, status, sync_status, int(limit))
    # SPECIFIC STATUS AND ALL CLIENTS
    elif status != "ALL" and client == "ALL" and sync_status == "ALL":
        query = "select client, start_ts, end_ts, status, duration, share, id, sync_status from events where status = '%s' order by start_ts desc limit %d" % (status, int(limit))
    # SPECIFIC SYNC_STATUS AND ALL CLIENTS
    elif sync_status != "ALL" and client == "ALL" and status == "ALL":
        query = "select client, start_ts, end_ts, status, duration, share, id, sync_status from events where sync_status = '%s' order by start_ts desc limit %d" % (sync_status, int(limit))
    # SPECIFIC SYNC_STATUS AND SPECIFIC STATUS
    elif sync_status != "ALL" and client == "ALL" and status != "ALL":
        query = "select client, start_ts, end_ts, status, duration, share, id, sync_status from events where sync_status = '%s' and status ='%s' order by start_ts desc limit %d" % (sync_status, status, int(limit))
    #print ("Query %s" % query)
    res = query_db(query)
    return res
