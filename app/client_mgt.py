import time
from db_conn import get_db, query_db


class ClientMgt(object):
    client = ""

    def __init__(self, client):
        self.client = client

    def lastseen(self):
        query = f"select end_ts from events where client='{self.client}' order by end_ts limit 1;"
        result = query_db(query)
        return result

    def info(self):
        result = {}
        query = f"select count(status) from events where client='{self.client}' and status='OK';"
        count_ok = query_db(query)[0]
        query = f"select count(status) from events where client='{self.client}' and status='KO';"
        count_ko = query_db(query)[0]
        #count_total = count_ok + count_ko
        query = f"select lastseen from clients where name='{self.client}';"
        lastseen = query_db(query)
        query = f"select joindate from clients where name='{self.client}';"
        joindate = query_db(query)
        query = f"select status from clients where name='{self.client}';"
        status = query_db(query)
        query = f"select ssh_key from clients where name='{self.client}';"
        ssh_key = query_db(query)
        query = f"select share from clients where name='{self.client}';"
        share = query_db(query)
        query = f"select threshold from clients where name='{self.client}';"
        threshold = query_db(query)
        query = f"select avg(duration) from events where client='{self.client}';"
        avg_duration = query_db(query)
        #print(f"last seen: {lastseen}, avg_sync: {avg_duration}")
        if not lastseen[0][0] or not avg_duration[0][0]:
            result.update({'share': share[0][0], 'ok': count_ok[0], 'ko': count_ko[0], 'total': count_ok[0]+count_ko[0],
                           'lastseen': 'Never', 'joindate': joindate[0][0], 'status': status[0][0], 'ssh_key': ssh_key[0][0],
                           'threshold': threshold[0][0], 'avg_duration': "None"})
        else:
            result.update({'share': share[0][0], 'ok': count_ok[0], 'ko': count_ko[0], 'total': count_ok[0]+count_ko[0],
                           'lastseen': lastseen[0][0], 'joindate': joindate[0][0], 'status': status[0][0], 'ssh_key': ssh_key[0][0],
                           'threshold': threshold[0][0], 'avg_duration': float("{0:.2f}".format(avg_duration[0][0]))})
        return result

    def status(self):
        query = f"select name,status from clients where name='{self.client}'"
        result = query_db(query)
        return result

    def exist(self):
        query = f"select count(name) from clients where name='{self.client}'"
        result = query_db(query)
        return result[0]

    def add(self, ssh_key, authkeyfile, register_type, share):
        result = []
        self.ssh_key = ssh_key
        self.authkeyfile = authkeyfile
        self.register_type = register_type
        self.share = share
        if register_type == "ui":
          result.append(self.add_to_db(self.register_type, self.ssh_key, self.share))
          result.append(self.add_to_keyfile(self.authkeyfile, self.ssh_key))
        elif register_type == "join":
          result.append(self.add_to_db(self.register_type, self.ssh_key, self.share))
        return result

    def add_to_db(self, register_type, ssh_key, share):
        self.ssh_key = ssh_key
        self.register_type = register_type
        self.share = share
        if register_type == "ui":
           status = "Active"
        else:
           status = "Registered"
        query = f"insert into clients (name,ssh_key,status,joindate,share,threshold) values ('{self.client}','{ssh_key}','{status}',{int(time.time())},'{share}',0)"
        #print (query)
        query_db(query)
        get_db().commit()
        return f"<br>Client {self.client} added to DB, status {status}"
    
    def add_to_keyfile(self, authkeyfile, ssh_key):
        self.ssh_key = ssh_key
        self.authkeyfile = authkeyfile
        print(ssh_key)
        auth_command = 'command="/usr/bin/unison -server"'
        with open (authkeyfile, 'a') as f:
          f.write(f"\n{auth_command} {ssh_key} CLIENT:{self.client}")
        return f"<br>Client {self.client} added to Authorized Keys"

    def activate(self, ssh_key, authkeyfile):
        self.ssh_key = ssh_key
        self.authkeyfile = authkeyfile
        result = []
        query = (f"update clients set status='Active' where name='{self.client}'")
        query_db(query)
        get_db().commit()
        result = [ "<br>Client activated on database" ]
        result.append(self.add_to_keyfile(self.authkeyfile, self.ssh_key))
        return result

    def set_threshold(self, threshold):
        self.threshold = threshold
        #print (threshold)
        query = (f"update clients set threshold={self.threshold} where name='{self.client}'")
        query_db(query)
        get_db().commit()
        return f"<br>Client {self.client} threshold set to {int(threshold)} seconds"

    def sync_status(self, type='db'):
        self.type = type
        if self.type == "db":
            query = f"select sync_status from clients where name='{self.client}';"
            status = query_db(query)
            return status[0][0]
        else:
           query = f"select threshold from clients where name='{self.client}';"
           threshold = query_db(query)
           query = f"select max(id),end_ts from events where client='{self.client}' and status='OK';"
           lastok = query_db(query)
           if lastok[0][0]:
              ts = int(time.time())
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
        #print(self.client)
        self.s_status = s_status
        current_status = self.sync_status()
        #print(current_status)
        if current_status != s_status:
           query = (f"update clients set sync_status='{self.s_status}' where name='{self.client}'")
           #print(query)
           query_db(query)
           get_db().commit()

    def check_pending(self):
        query = f"select * from events where client='{self.client}' and status='SYNCING';"
        brokensync=query_db(query)
        #print("Brokensync :%s" % brokensync)
        if brokensync != []:
           query = f"update events set status='KO', log='Sync was interrupted' where client='{self.client}' and status='SYNCING';"
           query_db(query)
           get_db().commit()

    def remove(self, authkeyfile):
        self.authkeyfile = authkeyfile
        query = f"delete from clients where name = '{self.client}'"
        query_db(query)
        get_db().commit()
        with open(authkeyfile, "r+") as f:
            new_f = f.readlines()
            f.seek(0)
            for line in new_f:
                if f"CLIENT:{self.client}" not in line:
                    f.write(line)
            f.truncate()

    def list_clients(self):
        query = "select name from clients order by name"
        clientlist = query_db(query)
        return clientlist

    def list_clists_to_register(self):
        query = "select count(id) from clients where status='Registered'"
        toregister = query_db(query)
        return toregister[0][0]

    def list_clients_threshold(self):
        query = "select name from clients where threshold !=0"
        clientlist = query_db(query)
        return clientlist

    def list_clients_page(self, orderby="id"):
        self.orderby = orderby
        query = (f"SELECT name,status,joindate,threshold,ssh_key,lastseen from clients order by {orderby};")
        print(query)
        res = query_db(query)
        return res

    def start_sync(self, start_ts, share, status="SYNCING"):
        self.start_ts = start_ts
        self.share = share
        self.status = status
        query = (f"insert into events (client,start_ts,share,status) values ('{self.client}',{start_ts},'{share}','{status}')")
        #print (query)
        query_db(query)
        get_db().commit()

    def end_sync(self, start_ts, end_ts, status, sync_status, log):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.status = status
        self.sync_status = sync_status
        self.log = log
        duration = self.end_ts - self.start_ts
        query = (f"update events set status='{status}', sync_status='{sync_status}', end_ts={end_ts}, duration={duration}, log='{log}' where client='{self.client}' and start_ts={start_ts}")
        query_db(query)
        get_db().commit()
        query = (f"update clients set lastseen='{end_ts}' where name='{self.client}'")
        query_db(query)
        get_db().commit()
