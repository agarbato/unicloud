import os
import errno
from db_conn import get_db, query_db
import shutil
import subprocess

class ShareMgt(object):
    share = ""
    def __init__(self, name):
      self***REMOVED***name = name
    def add(self, path, description, create):
      self***REMOVED***path = path
      self***REMOVED***description = description
      self***REMOVED***create = create
      exist = self***REMOVED***exist()
      if exist[0] == 1:
         print ("Share %s already exist" % exist)
         return False
      try:
          if self***REMOVED***create == "Yes":
           os***REMOVED***makedirs(self***REMOVED***path)
          self***REMOVED***add_to_db(self***REMOVED***path, self***REMOVED***description)
          return True
      except OSError as exception:
          if exception***REMOVED***errno != errno***REMOVED***EEXIST:
              raise
          else:
              return False                                         

    def share_list(self):
        query = "select name from shares"
        result = query_db(query)
        return result


    def info(self, info):
      self***REMOVED***info = info
      #print ("Info arrived: %s" % self***REMOVED***info)
      exist = self***REMOVED***exist()
      if exist[0] == 0:
         print ("exist %s" % exist)
         result = False
      else:
        if self***REMOVED***info == "all":
           result = {}
           query = "select name,path,description,size from shares where name='%s'" % self***REMOVED***name
           q = query_db(query)
           query2 = "select name from clients where share='%s'" % self***REMOVED***name
           q2 = query_db(query2)
           query3 = "select count(name) from clients where share='%s'" % self***REMOVED***name
           q3 = query_db(query3)
           #print (q2)
           client_list = [""***REMOVED***join(line) for line in q2]
           client_list_final = " - "
           client_list_final = client_list_final***REMOVED***join(client_list)
           result***REMOVED***update({'name': q[0][0], 'path': q[0][1], 'description': q[0][2], 'size': q[0][3], 'clients': client_list_final, 'clients_count': q3[0][0] })
        elif self***REMOVED***info == "path":
           #result=[]
           query = "select path from shares where name='%s'" % self***REMOVED***name
           q = query_db(query)
           #print ("Query: %s, Result: %s" % (query, q[0][0]))
           result = q[0][0]
        elif self***REMOVED***info == "size":
           #result=[]
           query = "select size from shares where name='%s'" % self***REMOVED***name
           q = query_db(query)
           #print ("Query: %s, Result: %s" % (query, q[0][0]))
           result = q[0][0]
      return result

    def add_to_db(self, path, description):
      self***REMOVED***path = path
      self***REMOVED***decription = description
      query = "insert into shares (name,path,description,size) values ('%s','%s','%s','None')" % (self***REMOVED***name, self***REMOVED***path, self***REMOVED***description)
      #print (query)
      query_db(query)
      get_db()***REMOVED***commit()

    def delete(self, path):
      self***REMOVED***path = path
      #dirpath = os***REMOVED***path***REMOVED***join('***REMOVED***/shares', self***REMOVED***path)
      if os***REMOVED***path***REMOVED***exists(self***REMOVED***path) and os***REMOVED***path***REMOVED***isdir(self***REMOVED***path):
          shutil***REMOVED***rmtree(self***REMOVED***path)
          self***REMOVED***delete_from_db()
          return True
      else:
          return False

    def delete_from_db(self, path):
        self***REMOVED***path = path
        query = "delete from shares where path = '%s'" % self***REMOVED***path
        query_db(query)
        get_db()***REMOVED***commit()

    def exist(self):
        query = "select count(name) from shares where name='%s'" % self***REMOVED***name
        result = query_db(query)
        return result[0]

    def getsize(self):
        result = []
        #print (self***REMOVED***name)
        shareinfo = self***REMOVED***info("all")
        #print(shareinfo)
        path = shareinfo['path']
        size = shareinfo['size']
        realsize = subprocess***REMOVED***check_output(['du', '-hs', path])***REMOVED***split()[0]***REMOVED***decode('utf-8')
        #print ("Size %s" % size)
        #print ("Realsize %s" % realsize)
        for r in realsize, size:
            result***REMOVED***append(r)
        return result

    def updatesize(self):
        #print (self***REMOVED***name)
        size = self***REMOVED***getsize()
        size_on_db = size[1]
        size_on_fs = size[0]
        #print ("Realsize %s" % realsize)
        #print ("Size %s " % size)
        if size_on_fs != size_on_db:
            query = "update shares set size='%s' where name='%s'" % (size_on_fs, self***REMOVED***name)
            #print (query)
            query_db(query)
            get_db()***REMOVED***commit()
        else:
            print("Size is the same, no need to update db")
