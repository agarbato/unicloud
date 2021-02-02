import time
import atexit
from db_conn import *
from flask import Flask, g, render_template, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_basicauth import BasicAuth
from flask_autoindex import AutoIndex
from client_mgt import ClientMgt
from share_mgt import ShareMgt
from homestats import *
from apscheduler***REMOVED***schedulers***REMOVED***background import BackgroundScheduler
from scheduler_tasks import *
from conf import *

root_dir = "/data"
database = root_dir + "/unicloud***REMOVED***db"
authkeyfile = root_dir + "/***REMOVED***ssh/unicloud_authorized_keys"
startTime = time***REMOVED***time()

init_db()
app = Flask(__name__, static_url_path='/static')
files_index = AutoIndex(app, shares_path, add_url_rules=False)
api = Api(app)

if server_debug:
    print ("Debug is active***REMOVED******REMOVED***")
    app***REMOVED***debug = True
    from werkzeug***REMOVED***debug import DebuggedApplication
    app***REMOVED***wsgi_app = DebuggedApplication(app***REMOVED***wsgi_app, True)
else:
    print("Debug is disabled***REMOVED******REMOVED***")

app***REMOVED***config['BASIC_AUTH_USERNAME'] = server_ui_username
app***REMOVED***config['BASIC_AUTH_PASSWORD'] = server_ui_password
basic_auth = BasicAuth(app)

# SCHEDULER

scheduler = BackgroundScheduler()
scheduler***REMOVED***add_job(func=scheduler_tasks_update_sync_status, trigger="interval", seconds=60, args=(app,))
scheduler***REMOVED***add_job(func=scheduler_tasks_share_update_size, trigger="interval", hours=6, args=(app,))
scheduler***REMOVED***add_job(func=scheduler_tasks_purge_logs, trigger="interval", hours=12, args=(app,))
scheduler***REMOVED***start()

# Shut down the scheduler when exiting the app
atexit***REMOVED***register(lambda: scheduler***REMOVED***shutdown())


### FILTERS

# helper to close
@app***REMOVED***teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
      db***REMOVED***close()


@app***REMOVED***template_filter('dt')
def _jinja2_filter_datetime(date, fmt=None):
    #date = int(time***REMOVED***time())
    if fmt:
        return time***REMOVED***strftime(fmt, time***REMOVED***localtime(date))
    if date is not None:
        return time***REMOVED***strftime("%Y-%m-%d %H:%M:%S", time***REMOVED***localtime(date))
    else:
        return "None"


@app***REMOVED***template_filter('inc')
def _jinja2_filter_inc(number):
   number += 1
   return number


@app***REMOVED***template_filter('dec')
def _jinja2_filter_dec(number):
    number -= 1
    return number


@app***REMOVED***template_filter('sync_status')
def _jinja2_filter_sync_status(client):
    #date = int(time***REMOVED***time())
    cl=ClientMgt(client)
    sync_status = cl***REMOVED***sync_status()
    #print ("Checking status for %s, status %s" % (client, sync_status)  )
    return sync_status

# HOME #


@app***REMOVED***route("/", methods=['GET'])
@basic_auth***REMOVED***required
def home():
    sys_stats = homestats_sys(startTime)
    unicloud_stats = homestats_unicloud()
    runtime_stats = homestats_runtime()
    return render_template("index***REMOVED***html", sys_stats=sys_stats, unicloud_stats=unicloud_stats, runtime_stats=runtime_stats)

# DOC #


@app***REMOVED***route("/doc", methods=['GET'])
@basic_auth***REMOVED***required
def doc():
    return render_template("doc***REMOVED***html")

# ABOUT #


@app***REMOVED***route("/about", methods=['GET'])
@basic_auth***REMOVED***required
def about():
    return render_template("about***REMOVED***html")


# FILES
# Custom indexing
@app***REMOVED***route('/files/<path:path>', strict_slashes=False)
@app***REMOVED***route("/files", strict_slashes=False, methods=['GET'])
@basic_auth***REMOVED***required
def autoindex(path='***REMOVED***'):
   return files_index***REMOVED***render_autoindex(path)

#### CLIENTS REQUESTS #########


@app***REMOVED***route("/status", methods=['GET'])
def status():
   return "[OK] Ready to serve sir***REMOVED******REMOVED***\n" , 200


@app***REMOVED***route("/clients", methods=['GET'])
@basic_auth***REMOVED***required
def clients():
    query = """ SELECT clients***REMOVED***name,
                  clients***REMOVED***status,
                  clients***REMOVED***joindate,
                  clients***REMOVED***threshold,
                  clients***REMOVED***ssh_key,
                  max(events***REMOVED***end_ts)
                FROM clients
                LEFT JOIN events on events***REMOVED***client = clients***REMOVED***name
                GROUP BY clients***REMOVED***name
                ORDER BY events***REMOVED***end_ts desc """
    res = query_db(query)
    #print (res)
    return render_template("clients***REMOVED***html", clients=res)


@app***REMOVED***route("/clients/mgt", methods=['GET'])
@basic_auth***REMOVED***required
def client_mgt():
    client = ClientMgt("all")
    clientlist = client***REMOVED***list_clients()
    share = ShareMgt("all")
    sharelist = share***REMOVED***share_list()
    return render_template("client_mgt***REMOVED***html", clientlist=clientlist, sharelist=sharelist)


@app***REMOVED***route("/clients/status/<client>", methods=['GET'])
def client_status(client):
    cl=ClientMgt(client)
    exist = cl***REMOVED***exist()
    if exist[0] == 0:
      return "Client %s does not exist, register first\n" % client, 404
    else:
      status=cl***REMOVED***status()
      #result="\n"***REMOVED***join(status[0])
      #print (status)
      if status[0][1] == "OK":
        return "Client %s status: [ %s ]\n" % (status[0][0], status[0][1]), 200
      else:
        return "Client %s need to be activated***REMOVED*** Activate from server UI!" % status[0][0], 401
      #return jsonify(status)


@app***REMOVED***route("/clients/info/<client>", methods=['GET'])
def client_info(client):
    cl = ClientMgt(client)
    exist = cl***REMOVED***exist()
    if exist[0] == 0:
      return "Client %s does not exist, register first\n" % client, 404
    else:
      status=cl***REMOVED***info()
      return jsonify(status)


@app***REMOVED***route("/clients/info/ui/<client>", methods=['GET'])
@basic_auth***REMOVED***required
def client_info_ui(client):
    cl=ClientMgt(client)
    exist = cl***REMOVED***exist()
    status = cl***REMOVED***info()
    #print (status)
    if status['threshold'] > 0:
      sync_status = cl***REMOVED***sync_status()
    else:
      sync_status = 0
    if exist[0] == 0:
      return "Client %s does not exist, register first\n" % client, 404
    else:
      status=cl***REMOVED***info()
      return render_template("client_info***REMOVED***html", status=status, client=client, sync_status=sync_status)


@app***REMOVED***route("/clients/register", methods=['POST'])
def client_register():
    name = request***REMOVED***form***REMOVED***get('name')
    ssh_key = request***REMOVED***form***REMOVED***get('ssh_key')
    share = request***REMOVED***form***REMOVED***get('share')
    register_type = "join"
    if name is not None and ssh_key is not None:
       client = ClientMgt(name)
       exist = client***REMOVED***exist()
       #print (exist)
       if exist[0] > 0:
           result = "Error Client %s already exist" % name
           rc = 500
       else:
           print(ssh_key)
           print(authkeyfile)
           client***REMOVED***add(ssh_key, authkeyfile, register_type, share)
           result = "Client %s added successfully, Activate it from server UI!" % name
           rc = 200
    else:
        result = "Incomplete request"
        rc = 500
    return jsonify(result), rc


@app***REMOVED***route("/clients/add/process", methods=['POST'])
@basic_auth***REMOVED***required
def client_process():
    name = request***REMOVED***form***REMOVED***get('name')
    ssh_key = request***REMOVED***form***REMOVED***get('ssh_key')
    share = request***REMOVED***form***REMOVED***get('share')
    register_type = "ui"
    if name is not None or ssh_key is not None:
       client = ClientMgt(name)
       if client***REMOVED***exist()[0] > 0:
           result = "Error Client %s already exist" % name
           rc = 500
       else:
           result = "\n"***REMOVED***join(client***REMOVED***add(ssh_key, authkeyfile, register_type, share))
           rc = 200
       return render_template("client_mgt_result***REMOVED***html", result=result), rc


@app***REMOVED***route("/clients/del/process", methods=['POST'])
@basic_auth***REMOVED***required
def del_process():
    name = request***REMOVED***form***REMOVED***get('del_name')
    if name is not None:
       client = ClientMgt(name)
       print (client***REMOVED***exist()[0])
       if client***REMOVED***exist()[0] == 0:
           result = "Client %s does not exist" % name
       else:
           client***REMOVED***remove(authkeyfile)
           result = "Client %s removed successfully" % name
       return render_template("client_mgt_result***REMOVED***html", result=result), 200


@app***REMOVED***route("/clients/activate/process", methods=['POST'])
@basic_auth***REMOVED***required
def activate_process():
    name = request***REMOVED***form***REMOVED***get('name')
    ssh_key = request***REMOVED***form***REMOVED***get('ssh_key')
    if name is not None:
       client = ClientMgt(name)
       result = "\n"***REMOVED***join(client***REMOVED***activate(ssh_key,authkeyfile))
       print (result)
       return render_template("client_activate_result***REMOVED***html", result=result), 200


@app***REMOVED***route("/clients/threshold/process", methods=['POST'])
@basic_auth***REMOVED***required
def set_threshold():
    name = request***REMOVED***form***REMOVED***get('name')
    threshold = request***REMOVED***form***REMOVED***get('threshold')
    client = ClientMgt(name)
    result = client***REMOVED***set_threshold(int(threshold))
    print (result)
    return render_template("client_threshold_result***REMOVED***html", result=result, name=name), 200

#### SHARES REQUESTS ######


@app***REMOVED***route("/shares", methods=['GET'])
@basic_auth***REMOVED***required
def shares():
    query = "select name, description, size, path from shares"
    res = query_db(query)
    return render_template("shares***REMOVED***html", shares=res)


@app***REMOVED***route("/shares/info/ui/<name>", methods=['GET'])
@basic_auth***REMOVED***required
def shares_info_ui(name):
    info = "all"
    share = ShareMgt(name)
    result = share***REMOVED***info(info)
    if not result:
      result = "Error, %s does not exist\n" % name
      return result, 404
    else:
      return render_template("share_info***REMOVED***html", share=result)


@app***REMOVED***route("/shares/info/<name>")
def share_info(name):
    info = "all"
    share = ShareMgt(name)
    result = share***REMOVED***info(info)
    if not result:
      result = "Error, %s does not exist\n" % name
      return result, 404
    else:
      return jsonify(result), 200


@app***REMOVED***route("/shares/info/<name>/path")
def share_info_path(name):
    info = "path"
    share = ShareMgt(name)
    result = share***REMOVED***info(info)
    if not result:
      result = "Error, %s does not exist\n" % name
      return result, 404
    else:
      return result + "\n", 200


@app***REMOVED***route("/shares/mgt", methods=['GET'])
@basic_auth***REMOVED***required
def share_mgt():
    share = ShareMgt("all")
    sharelist = share***REMOVED***share_list()
    return render_template("share_mgt***REMOVED***html", shares_path=shares_path, sharelist=sharelist)


@app***REMOVED***route("/shares/add/process", methods=['POST'])
@basic_auth***REMOVED***required
def share_add_process():
    name = request***REMOVED***form***REMOVED***get('name')
    path = request***REMOVED***form***REMOVED***get('path')
    description = request***REMOVED***form***REMOVED***get('description')
    ssh_key = request***REMOVED***form***REMOVED***get('ssh_key')
    create = request***REMOVED***form***REMOVED***get('create')
    if name is not None or path is not None or description is not None:
       share = ShareMgt(name)
       result = share***REMOVED***add(path, description, create)
       #print (result)
       if result is not True:
           result = "Error, share %s or path %s already exist" % (name, path)
           rc = 500
       else:
           result = "Share %s added successfully<br>Path: %s" % ( name, path)
           rc = 200
    else:
       result = "Please Fill all the fields in the form***REMOVED******REMOVED******REMOVED***"
    return render_template("share_mgt_result***REMOVED***html", result=result), rc


@app***REMOVED***route("/shares/del/process", methods=['POST'])
@basic_auth***REMOVED***required
def share_del_process():
    name = request***REMOVED***form***REMOVED***get('name')
    path = request***REMOVED***form***REMOVED***get('path')
    delete = request***REMOVED***form***REMOVED***get('delete')
    if name is not None or path is not None:
       share = ShareMgt(name)
       result = share***REMOVED***delete(path, description)
       print (result)
       if result is not True:
           result = "Error, Path %s does not exist or share not present" % path
           rc = 500
       else:
           result = "Share %s Removed successfully\n Path: %s" % (name, path)
           rc = 200
    else:
       result = "Please Fill all the fields in the form***REMOVED******REMOVED******REMOVED***"
    return render_template("share_mgt_result***REMOVED***html", result=result), rc


@app***REMOVED***route("/shares/getsize/<name>/process", methods=['POST'])
@basic_auth***REMOVED***required
def share_get_size_process(name):
    share = ShareMgt(name)
    share***REMOVED***getsize()
    result = "Refreshing Share %s size" % name
    return render_template("share_mgt_result***REMOVED***html", result=result), 200


@app***REMOVED***route("/shares/exist", methods=['POST'])
def shares_exist():
    path = request***REMOVED***form***REMOVED***get('path')
    if path is not None:
       share = ShareMgt('', path, '')
       exist = share***REMOVED***exist()
       #print (exist)
       if exist[0] == 0:
           result = "Error, share %s does not exist" % path
           rc = 500
       else:
           result = "Ok share %s exist!" % path
           rc = 200
    else:
        result = "Incomplete request"
        rc = 500
    return jsonify(result), rc

#### EVENTS HTML ##########

@app***REMOVED***route("/events", methods=['PUT','POST','GET'])
@basic_auth***REMOVED***required
def events():
    client = request***REMOVED***form***REMOVED***get('client')
    status = request***REMOVED***form***REMOVED***get('status')
    sync_status = request***REMOVED***form***REMOVED***get('sync_status')
    limit = request***REMOVED***form***REMOVED***get('limit')
    #print ("Client %s, Status %s" % (client, status) )
    if limit is None:
      limit = 50
    #print ("Client %s Status %s" % (client,status))

    # ALL RESULTS
    if client == "ALL" and  status == "ALL" and sync_status== "ALL" or client is None and status is None and sync_status is None: # ALL RESULTS
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
    client = ClientMgt("all")
    clientlist = client***REMOVED***list_clients()
    return render_template("events***REMOVED***html", events=res, clientlist=clientlist), 200


@app***REMOVED***route("/events/<id>", methods=['GET'])
@basic_auth***REMOVED***required
def event_id(id):
    query = "select count(id) from events where id=%d and status is not 'SYNCING'" % int(id)
    if int(query_db(query)[0][0]) > 0:
       query = "select id,client,status,log,start_ts,end_ts,duration,share from events where id=%d" % int(id)
       res = query_db(query)
       return render_template("event_log***REMOVED***html", event=res)
    else:
       return render_template("event_404***REMOVED***html", id=int(id)), 404

####  SYNC ENDPOINTS ####


@app***REMOVED***route("/sync/start/<client>", methods=['PUT','POST'])
def sync_start(client):
    share = request***REMOVED***form***REMOVED***get('share')
    start_ts = int(request***REMOVED***form***REMOVED***get('start_ts'))
    clientmgt = ClientMgt(client)
    #print("Start Sync")
    if clientmgt***REMOVED***exist()[0] == 0:
      return "Client %s does not exist, register first" % client, 500
    else:
      clientmgt***REMOVED***check_pending()
      clientmgt***REMOVED***start_sync(start_ts, share)
      return "Sync Started, record updated with status %s" % status, 200


@app***REMOVED***route("/sync/end/<client>", methods=['PUT','POST'])
def sync_end(client):
    start_ts = int(request***REMOVED***form***REMOVED***get('start_ts'))
    status = request***REMOVED***form***REMOVED***get('status')
    sync_status = request***REMOVED***form***REMOVED***get('sync_status')
    log = request***REMOVED***form***REMOVED***get('log')
    end_ts = int(request***REMOVED***form***REMOVED***get('end_ts'))
    clientmgt = ClientMgt(client)
    #print("End Sync")
    #print("%s : Log Sync Enc Received: %s" % (client, log) )
    if clientmgt***REMOVED***exist()[0] == 0:
      return "Client %s does not exist, register first" % client, 500
    else:
      clientmgt***REMOVED***end_sync(start_ts, end_ts, status, sync_status, log)
      return "Sync Terminated, record updated with status %s" % status, 201

############

#app***REMOVED***run(debug=True,port=8080)
