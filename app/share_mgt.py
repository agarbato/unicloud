import os
import errno
from db_conn import get_db, query_db
import shutil
import subprocess

class ShareMgt(object):
    share = ""
    def __init__(self, name):
      self.name = name
    def add(self, path, description, create):
      self.path = path
      self.description = description
      self.create = create
      exist = self.exist()
      if exist[0] == 1:
         print ("Share %s already exist" % exist)
         return False
      try:
          if self.create == "Yes":
           os.makedirs(self.path)
          self.add_to_db(self.path, self.description)
          return True
      except OSError as exception:
          if exception.errno != errno.EEXIST:
              raise
          else:
              return False                                         

    def share_list(self):
        query = "select name from shares"
        result = query_db(query)
        return result


    def info(self, info):
      self.info = info
      #print ("Info arrived: %s" % self.info)
      exist = self.exist()
      if exist[0] == 0:
         print ("exist %s" % exist)
         result = False
      else:
        if self.info == "all":
           result = {}
           query = "select name,path,description,size from shares where name='%s'" % self.name
           q = query_db(query)
           query2 = "select name from clients where share='%s'" % self.name
           q2 = query_db(query2)
           query3 = "select count(name) from clients where share='%s'" % self.name
           q3 = query_db(query3)
           #print (q2)
           client_list = ["".join(line) for line in q2]
           client_list_final = " - "
           client_list_final = client_list_final.join(client_list)
           result.update({'name': q[0][0], 'path': q[0][1], 'description': q[0][2], 'size': q[0][3], 'clients': client_list_final, 'clients_count': q3[0][0] })
        elif self.info == "path":
           #result=[]
           query = "select path from shares where name='%s'" % self.name
           q = query_db(query)
           #print ("Query: %s, Result: %s" % (query, q[0][0]))
           result = q[0][0]
        elif self.info == "size":
           #result=[]
           query = "select size from shares where name='%s'" % self.name
           q = query_db(query)
           #print ("Query: %s, Result: %s" % (query, q[0][0]))
           result = q[0][0]
      return result

    def add_to_db(self, path, description):
      self.path = path
      self.decription = description
      query = "insert into shares (name,path,description,size) values ('%s','%s','%s','None')" % (self.name, self.path, self.description)
      #print (query)
      query_db(query)
      get_db().commit()

    def delete(self, path):
      self.path = path
      #dirpath = os.path.join('./shares', self.path)
      if os.path.exists(self.path) and os.path.isdir(self.path):
          shutil.rmtree(self.path)
          self.delete_from_db()
          return True
      else:
          return False

    def delete_from_db(self, path):
        self.path = path
        query = "delete from shares where path = '%s'" % self.path
        query_db(query)
        get_db().commit()

    def exist(self):
        query = "select count(name) from shares where name='%s'" % self.name
        result = query_db(query)
        return result[0]

    def getsize(self):
        result = []
        #print (self.name)
        shareinfo = self.info("all")
        #print(shareinfo)
        path = shareinfo['path']
        size = shareinfo['size']
        realsize = subprocess.check_output(['du', '-hs', path]).split()[0].decode('utf-8')
        #print ("Size %s" % size)
        #print ("Realsize %s" % realsize)
        for r in realsize, size:
            result.append(r)
        return result

    def updatesize(self):
        #print (self.name)
        size = self.getsize()
        size_on_db = size[1]
        size_on_fs = size[0]
        #print ("Realsize %s" % realsize)
        #print ("Size %s " % size)
        if size_on_fs != size_on_db:
            query = "update shares set size='%s' where name='%s'" % (size_on_fs, self.name)
            #print (query)
            query_db(query)
            get_db().commit()
        else:
            print("Size is the same, no need to update db")
