import time
from db_conn import get_db, query_db


class ClientMgt(object):
    client = ""
    def __init__(self, client):
        self***REMOVED***client = client

    def lastseen(self):
        query = "select end_ts from events where client='%s' order by end_ts limit 1;" % self***REMOVED***client
        result = query_db(query)
        return result

    def info(self):
        result = {}
        query = "select count(status) from events where client='%s' and status='OK';" %self***REMOVED***client
        count_ok=query_db(query)[0]
        query = "select count(status) from events where client='%s' and status='KO';" %self***REMOVED***client
        count_ko = query_db(query)[0]
        #count_total = count_ok + count_ko
        query = "select end_ts from events where client='%s' order by id desc limit 1;" %self***REMOVED***client
        lastseen = query_db(query)
        query = "select joindate from clients where name='%s';" % self***REMOVED***client
        joindate = query_db(query)
        query = "select status from clients where name='%s';" % self***REMOVED***client
        status = query_db(query)
        query = "select ssh_key from clients where name='%s';" % self***REMOVED***client
        ssh_key = query_db(query)
        query = "select share from clients where name='%s';" % self***REMOVED***client
        share = query_db(query)
        query = "select threshold from clients where name='%s';" % self***REMOVED***client
        threshold = query_db(query)
        #print ("last seen: %s" % lastseen)
        query = "select avg(duration) from events where client='%s';" % self***REMOVED***client
        avg_duration = query_db(query)
        if lastseen == []:
            result***REMOVED***update({'share': share[0][0], 'ok': count_ok[0], 'ko': count_ko[0], 'total': count_ok[0]+count_ko[0],
                           'lastseen': 'Never', 'joindate': joindate[0][0], 'status': status[0][0], 'ssh_key': ssh_key[0][0],
                           'threshold': threshold[0][0], 'avg_duration': "None" })
        else:
            result***REMOVED***update({'share': share[0][0], 'ok': count_ok[0], 'ko': count_ko[0], 'total': count_ok[0]+count_ko[0],
                           'lastseen': lastseen[0][0], 'joindate': joindate[0][0], 'status': status[0][0], 'ssh_key': ssh_key[0][0],
                           'threshold': threshold[0][0], 'avg_duration': float("{0:***REMOVED***2f}"***REMOVED***format(avg_duration[0][0]))})
        return result

    def status(self):
        query = "select name,status from clients where name='%s'" % self***REMOVED***client
        result = query_db(query)
        return result

    def exist(self):
        query = "select count(name) from clients where name='%s'" % self***REMOVED***client
        result = query_db(query)
        return result[0]

    def add(self, ssh_key, authkeyfile, register_type, share):
        result = []
        self***REMOVED***ssh_key = ssh_key
        self***REMOVED***authkeyfile = authkeyfile
        self***REMOVED***register_type = register_type
        self***REMOVED***share = share
        if register_type == "ui":
          result***REMOVED***append(self***REMOVED***add_to_db(self***REMOVED***register_type, self***REMOVED***ssh_key, self***REMOVED***share))
          result***REMOVED***append(self***REMOVED***add_to_keyfile(self***REMOVED***authkeyfile, self***REMOVED***ssh_key))
        elif register_type == "join":
          result***REMOVED***append(self***REMOVED***add_to_db(self***REMOVED***register_type, self***REMOVED***ssh_key, self***REMOVED***share))
        return result

    def add_to_db(self, register_type, ssh_key, share):
        self***REMOVED***ssh_key = ssh_key
        self***REMOVED***register_type = register_type
        self***REMOVED***share = share
        if register_type == "ui":
           status = "Active"
        else:
           status = "Registered"
        query = "insert into clients (name,ssh_key,status,joindate,share,threshold) values ('%s','%s','%s',%d,'%s',0)" % (self***REMOVED***client, ssh_key, status, int(time***REMOVED***time()), share)
        #print (query)
        query_db(query)
        get_db()***REMOVED***commit()
        return "<br>Client %s added to DB, status %s" % ( self***REMOVED***client, status )
    
    def add_to_keyfile(self, authkeyfile, ssh_key):
        self***REMOVED***ssh_key = ssh_key
        self***REMOVED***authkeyfile = authkeyfile
        print (ssh_key)
        auth_command = 'command="/usr/bin/unison -server"'
        with open (authkeyfile, 'a') as f:
          f***REMOVED***write("\n" + auth_command + " " + ssh_key + " CLIENT:%s" % self***REMOVED***client)
        return "<br>Client %s added to Authorized Keys" % self***REMOVED***client

    def activate(self, ssh_key, authkeyfile):
        self***REMOVED***ssh_key = ssh_key
        self***REMOVED***authkeyfile = authkeyfile
        result=[]
        query = ("update clients set status='Active' where name='%s'") % self***REMOVED***client
        query_db(query)
        get_db()***REMOVED***commit()
        result = [ "<br>Client activated on database" ]
        result***REMOVED***append(self***REMOVED***add_to_keyfile(self***REMOVED***authkeyfile, self***REMOVED***ssh_key))
        return result

    def set_threshold(self, threshold):
        self***REMOVED***threshold = threshold
        #print (threshold)
        query = ("update clients set threshold=%d where name='%s'") % (self***REMOVED***threshold, self***REMOVED***client)
        query_db(query)
        get_db()***REMOVED***commit()
        return "<br>Client %s threshold set to %d seconds" % (self***REMOVED***client, int(threshold))

    def sync_status(self, type='db'):
        self***REMOVED***type = type
        if self***REMOVED***type == "db":
            query = "select sync_status from clients where name='%s';" % self***REMOVED***client
            status = query_db(query)
            return status[0][0]
        else:
           query = "select threshold from clients where name='%s';" % self***REMOVED***client
           threshold = query_db(query)
           query = "select max(id),end_ts from events where client='%s' and status='OK';" % self***REMOVED***client
           lastok = query_db(query)
           if lastok[0][0]:
              ts = int(time***REMOVED***time())
              delta = ts - lastok[0][1]
              if delta <= threshold[0][0]:
                return "In Sync"
              else:
                return "Out of Sync"
           else:
              return "Never synced"
           #print ("Delta is %d, Lastok: %d, Threshold is %d," % ( delta, lastok[0][0], threshold[0][0] ))
           #print ("LastOk %d" % lastok[0][0])
           #print ("Threshold %d" % threshold[0][0])

    def update_sync_status(self, s_status):
        #print(self***REMOVED***client)
        self***REMOVED***s_status = s_status
        current_status = self***REMOVED***sync_status()
        #print(current_status)
        if current_status != s_status:
           query = ("update clients set sync_status='%s' where name='%s'") % (self***REMOVED***s_status, self***REMOVED***client)
           #print(query)
           query_db(query)
           get_db()***REMOVED***commit()

    def check_pending(self):
        query="select * from events where client='%s' and status='SYNCING';" % self***REMOVED***client
        brokensync=query_db(query)
        #print("Brokensync :%s" % brokensync)
        if brokensync != []:
           query="update events set status='KO', log='Sync was interrupted' where client='%s' and status='SYNCING';" % self***REMOVED***client
           query_db(query)
           get_db()***REMOVED***commit()

    def remove(self, authkeyfile):
        self***REMOVED***authkeyfile = authkeyfile
        query = "delete from clients where name = '%s'" % self***REMOVED***client
        query_db(query)
        get_db()***REMOVED***commit()
        with open(authkeyfile, "r+") as f:
            new_f = f***REMOVED***readlines()
            f***REMOVED***seek(0)
            for line in new_f:
                if "CLIENT:%s" % self***REMOVED***client not in line:
                    f***REMOVED***write(line)
            f***REMOVED***truncate()

    def list_clients(self):
        query = "select name from clients"
        clientlist = query_db(query)
        return clientlist

    def list_clients_threshold(self):
        query = "select name from clients where threshold !=0"
        clientlist = query_db(query)
        return clientlist

    def start_sync(self, start_ts, share, status="SYNCING"):
        self***REMOVED***start_ts = start_ts
        self***REMOVED***share = share
        self***REMOVED***status = status
        query = ("insert into events (client,start_ts,share,status) values ('%s',%d,'%s','%s')") % (self***REMOVED***client, start_ts, share, status)
        #print (query)
        query_db(query)
        get_db()***REMOVED***commit()

    def end_sync(self, start_ts, end_ts, status, sync_status, log):
        self***REMOVED***start_ts = start_ts
        self***REMOVED***end_ts = end_ts
        self***REMOVED***status = status
        self***REMOVED***sync_status = sync_status
        self***REMOVED***log = log
        duration = self***REMOVED***end_ts - self***REMOVED***start_ts
        query = ("update events set status='%s', sync_status='%s', end_ts=%d, duration=%d, log='%s' where client='%s' and start_ts=%d") % (status, sync_status, end_ts, duration, log, self***REMOVED***client, start_ts)
        query_db(query)
        get_db()***REMOVED***commit()
