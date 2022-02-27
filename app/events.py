from db_conn import get_db, query_db

class Event(object):
    eventid = ""

    def __init__(self, eventid):
        self.eventid = int(eventid)

    def exist(self):
        query = f"select count(id) from events where id={self.eventid} and status is not 'SYNCING'"
        if query_db(query)[0][0] > 0:
            return True
        else:
            return False

    def info(self):
        query = f"select id,client,status,log,start_ts,end_ts,duration,share from events where id={self.eventid}"
        res = query_db(query)
        return res


def event_form(client, status, sync_status, limit=50):
    #select client, start_ts, end_ts, status, duration, share, id, sync_status from events where id > (select max(id-50) from events) order by start_ts desc;
    # ALL RESULTS
    if client == "ALL" and status == "ALL" and sync_status == "ALL" or client is None and status is None and sync_status is None: # ALL RESULTS
        query = f"select client, start_ts, end_ts, status, duration, share, id, sync_status from events where id > (select max(id-{limit}) from events) order by start_ts desc"
    # SPECIFIC CLIENT AND ALL STATUS AND ALL SYNC_STATUS
    elif client != "ALL" and status == "ALL" and sync_status == "ALL":
        query = f"select client, start_ts, end_ts, status, duration, share, id, sync_status from events where client='{client}' order by start_ts desc limit {limit}"
    # SPECIFIC CLIENT AND SPECIFIC STATUS AND ALL SYNC_STATUS
    elif client != "ALL" and status != "ALL" and sync_status == "ALL":
        query = f"select client, start_ts, end_ts, status, duration, share, id, sync_status from events where client='{client}' and status = '{status}' order by start_ts desc limit {limit}"
    # SPECIFIC CLIENT AND SPECIFIC SYNC_STATUS AND ALL STATUS
    elif client != "ALL" and sync_status != "ALL" and status == "ALL":
        query = f"select client, start_ts, end_ts, status, duration, share, id, sync_status from events where client='{client}' and sync_status='{sync_status}' order by start_ts desc limit {limit}"
    # SPECIFIC CLIENT AND SPECIFIC STATUS AND SPECIFIC SYNC_STATUS
    elif client != "ALL" and status != "ALL" and sync_status != "ALL":
        query = f"select client, start_ts, end_ts, status, duration, share, id, sync_status from events where client='{client}' and status='{status}' and sync_status='{sync_status}' order by start_ts desc limit {limit}"
    # SPECIFIC STATUS AND ALL CLIENTS
    elif status != "ALL" and client == "ALL" and sync_status == "ALL":
        query = f"select client, start_ts, end_ts, status, duration, share, id, sync_status from events where status='{status}' order by start_ts desc limit {limit}"
    # SPECIFIC SYNC_STATUS AND ALL CLIENTS
    elif sync_status != "ALL" and client == "ALL" and status == "ALL":
        query = f"select client, start_ts, end_ts, status, duration, share, id, sync_status from events where sync_status='{sync_status}' order by start_ts desc limit {limit}"
    # SPECIFIC SYNC_STATUS AND SPECIFIC STATUS
    elif sync_status != "ALL" and client == "ALL" and status != "ALL":
        query = f"select client, start_ts, end_ts, status, duration, share, id, sync_status from events where sync_status='{sync_status}' and status='{status}' order by start_ts desc limit {limit}"
    #print ("Query %s" % query)
    res = query_db(query)
    return res
