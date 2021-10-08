import time
import atexit
from db_conn import *
from flask import Flask, g, render_template, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_basicauth import BasicAuth
from flask_autoindex import AutoIndex
from client_mgt import ClientMgt
from share_mgt import ShareMgt
from events import Event, event_form
from homestats import *
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler_tasks import *
from time import strftime
from conf import *

time_format = "[%Y:%m:%d %H:%M:%S]"
root_dir = "/data"
database = root_dir + "/unicloud.db"
authkeyfile = root_dir + "/.ssh/unicloud_authorized_keys"
startTime = time.time()

init_db()
app = Flask(__name__, static_url_path='/static')
files_index = AutoIndex(app, shares_path, add_url_rules=False)
api = Api(app)

if server_debug:
    print(f"{strftime(time_format)} - App Debug is active")
    app.debug = True
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
else:
    print(f"{strftime(time_format)} - App Debug is disabled")

app.config['BASIC_AUTH_USERNAME'] = server_ui_username
app.config['BASIC_AUTH_PASSWORD'] = server_ui_password
basic_auth = BasicAuth(app)

# SCHEDULER

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduler_tasks_update_sync_status, trigger="interval", seconds=60, args=(app,))
if home_assistant:
    print(f"{strftime(time_format)} - Home assistant integration is active")
    scheduler.add_job(func=scheduler_tasks_update_home_assistant_clients, trigger="interval", seconds=home_assistant_push_interval, args=(app,))
    scheduler.add_job(func=scheduler_tasks_update_home_assistant_server, trigger="interval", seconds=home_assistant_push_interval, args=(app, startTime))
    scheduler.add_job(func=scheduler_tasks_update_home_assistant_shares, trigger="interval", seconds=home_assistant_push_interval, args=(app,))
scheduler.add_job(func=scheduler_tasks_share_update_size, trigger="interval", hours=6, args=(app,))
scheduler.add_job(func=scheduler_tasks_purge_logs, trigger="interval", hours=12, args=(app,))

scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


### FILTERS

# helper to close
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
      db.close()


@app.template_filter('dt')
def _jinja2_filter_datetime(date, fmt=None):
    #date = int(time.time())
    if fmt:
        return time.strftime(fmt, time.localtime(date))
    if date is not None:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(date))
    else:
        return "None"


@app.template_filter('inc')
def _jinja2_filter_inc(number):
   number += 1
   return number


@app.template_filter('dec')
def _jinja2_filter_dec(number):
    number -= 1
    return number


@app.template_filter('sync_status')
def _jinja2_filter_sync_status(client):
    #date = int(time.time())
    cl = ClientMgt(client)
    sync_status = cl.sync_status()
    #print ("Checking status for %s, status %s" % (client, sync_status)  )
    return sync_status


@app.template_filter('get_share_path')
def _jinja2_filter_get_share_path(share):
    s = ShareMgt(share)
    share_path = s.info(info="path")
    return share_path


# HOME #

@app.route("/", methods=['GET'])
@basic_auth.required
def home():
    sys_stats = homestats_sys(startTime)
    unicloud_stats = homestats_unicloud()
    runtime_stats = homestats_runtime()
    return render_template("index.html", sys_stats=sys_stats, unicloud_stats=unicloud_stats, runtime_stats=runtime_stats)

# DOC #


@app.route("/doc", methods=['GET'])
@basic_auth.required
def doc():
    return render_template("doc.html")

# ABOUT #


@app.route("/about", methods=['GET'])
@basic_auth.required
def about():
    return render_template("about.html")


# FILES
# Custom indexing
@app.route('/files/<path:path>', strict_slashes=False)
@app.route("/files", strict_slashes=False, methods=['GET'])
@basic_auth.required
def autoindex(path='.'):
   return files_index.render_autoindex(path)

#### CLIENTS REQUESTS #########


@app.route("/status", methods=['GET'])
def status():
   return "[OK] Ready to serve sir..\n" , 200


@app.route("/clients", methods=['GET'])
@basic_auth.required
def clients():
    client = ClientMgt("all-clients-page")
    res = client.list_clients_page()
    #print (res)
    return render_template("clients.html", clients=res)


@app.route("/clients/mgt", methods=['GET'])
@basic_auth.required
def client_mgt():
    client = ClientMgt("all")
    clientlist = client.list_clients()
    share = ShareMgt("all")
    sharelist = share.share_list()
    return render_template("client_mgt.html", clientlist=clientlist, sharelist=sharelist)


@app.route("/clients/status/<client>", methods=['GET'])
def client_status(client):
    cl = ClientMgt(client)
    exist = cl.exist()
    if exist[0] == 0:
      return "Client %s does not exist, register first\n" % client, 404
    else:
      status=cl.status()
      #result="\n".join(status[0])
      #print (status)
      if status[0][1] == "OK":
        return "Client %s status: [ %s ]\n" % (status[0][0], status[0][1]), 200
      else:
        return "Client %s need to be activated. Activate from server UI!" % status[0][0], 401
      #return jsonify(status)


@app.route("/clients/info/<client>", methods=['GET'])
def client_info(client):
    cl = ClientMgt(client)
    exist = cl.exist()
    if exist[0] == 0:
      return "Client %s does not exist, register first\n" % client, 404
    else:
      status = cl.info()
      return jsonify(status)


@app.route("/clients/info/ui/<client>", methods=['GET'])
@basic_auth.required
def client_info_ui(client):
    cl=ClientMgt(client)
    exist = cl.exist()
    status = cl.info()
    #print (status)
    if status['threshold'] > 0:
      sync_status = cl.sync_status()
    else:
      sync_status = 0
    if exist[0] == 0:
      return "Client %s does not exist, register first\n" % client, 404
    else:
      status = cl.info()
      return render_template("client_info.html", status=status, client=client, sync_status=sync_status)


@app.route("/clients/register", methods=['POST'])
def client_register():
    name = request.form.get('name')
    ssh_key = request.form.get('ssh_key')
    share = request.form.get('share')
    register_type = "join"
    if name is not None and ssh_key is not None:
       client = ClientMgt(name)
       exist = client.exist()
       #print (exist)
       if exist[0] > 0:
           result = "Error Client %s already exist" % name
           rc = 500
       else:
           print(ssh_key)
           print(authkeyfile)
           client.add(ssh_key, authkeyfile, register_type, share)
           result = "Client %s added successfully, Activate it from server UI!" % name
           rc = 200
    else:
        result = "Incomplete request"
        rc = 500
    return jsonify(result), rc


@app.route("/clients/add/process", methods=['POST'])
@basic_auth.required
def client_process():
    name = request.form.get('name')
    ssh_key = request.form.get('ssh_key')
    share = request.form.get('share')
    register_type = "ui"
    if name is not None or ssh_key is not None:
       client = ClientMgt(name)
       if client.exist()[0] > 0:
           result = "Error Client %s already exist" % name
           rc = 500
       else:
           result = "\n".join(client.add(ssh_key, authkeyfile, register_type, share))
           rc = 200
       return render_template("client_mgt_result.html", result=result), rc


@app.route("/clients/del/process", methods=['POST'])
@basic_auth.required
def del_process():
    name = request.form.get('del_name')
    if name is not None:
       client = ClientMgt(name)
       print (client.exist()[0])
       if client.exist()[0] == 0:
           result = "Client %s does not exist" % name
       else:
           client.remove(authkeyfile)
           result = "Client %s removed successfully" % name
       return render_template("client_mgt_result.html", result=result), 200


@app.route("/clients/activate/process", methods=['POST'])
@basic_auth.required
def activate_process():
    name = request.form.get('name')
    ssh_key = request.form.get('ssh_key')
    if name is not None:
       client = ClientMgt(name)
       result = "\n".join(client.activate(ssh_key,authkeyfile))
       print (result)
       return render_template("client_activate_result.html", result=result), 200


@app.route("/clients/threshold/process", methods=['POST'])
@basic_auth.required
def set_threshold():
    name = request.form.get('name')
    threshold = request.form.get('threshold')
    client = ClientMgt(name)
    result = client.set_threshold(int(threshold))
    print (result)
    return render_template("client_threshold_result.html", result=result, name=name), 200

#### SHARES REQUESTS ######


@app.route("/shares", methods=['GET'])
@basic_auth.required
def shares():
    shares = ShareMgt("all")
    res = shares.list_all_info()
    return render_template("shares.html", shares=res)


@app.route("/shares/info/ui/<name>", methods=['GET'])
@basic_auth.required
def shares_info_ui(name):
    info = "all"
    share = ShareMgt(name)
    result = share.info(info)
    if not result:
      result = "Error, %s does not exist\n" % name
      return result, 404
    else:
      return render_template("share_info.html", share=result)


@app.route("/shares/info/<name>")
def share_info(name):
    info = "all"
    share = ShareMgt(name)
    result = share.info(info)
    if not result:
      result = "Error, %s does not exist\n" % name
      return result, 404
    else:
      return jsonify(result), 200


@app.route("/shares/info/<name>/path")
def share_info_path(name):
    info = "path"
    share = ShareMgt(name)
    result = share.info(info)
    if not result:
      result = "Error, %s does not exist\n" % name
      return result, 404
    else:
      return result + "\n", 200


@app.route("/shares/mgt", methods=['GET'])
@basic_auth.required
def share_mgt():
    share = ShareMgt("all")
    sharelist = share.share_list()
    print(sharelist)
    return render_template("share_mgt.html", shares_path=shares_path, sharelist=sharelist)


@app.route("/shares/add/process", methods=['POST'])
@basic_auth.required
def share_add_process():
    name = request.form.get('name')
    path = request.form.get('path')
    description = request.form.get('description')
    create = request.form.get('create')
    if name is not None or path is not None or description is not None:
       share = ShareMgt(name)
       result = share.add(path, description, create)
       #print (result)
       if result is not True:
           result = "Error, share %s or path %s already exist" % (name, path)
           rc = 500
       else:
           result = "Share %s added successfully<br>Path: %s" % ( name, path)
           rc = 200
    else:
       result = "Please Fill all the fields in the form..."
    return render_template("share_mgt_result.html", result=result), rc


@app.route("/shares/del/process", methods=['POST'])
@basic_auth.required
def share_del_process():
    name = request.form.get('name')
    s = ShareMgt(name)
    path = s.info(info="path")
    delete_folder = request.form.get('delete_folder')
    result = s.delete(path, delete_folder)
    if result is not True:
       result = f"Error, Path {path} does not exist or share not present"
       rc = 500
    else:
       if delete_folder != "Yes":
          result = f"Share {name} Removed successfully<br>Existing Files on Path: {path} were not removed"
       else:
          result = f"Share {name} Removed successfully<br>All Files on Path: {path} removed"
       rc = 200
    return render_template("share_mgt_result.html", result=result), rc


@app.route("/shares/getsize/<name>/process", methods=['POST'])
@basic_auth.required
def share_get_size_process(name):
    share = ShareMgt(name)
    share.updatesize()
    result = "Refreshing Share %s size" % name
    return render_template("share_mgt_result.html", result=result), 200


@app.route("/shares/exist", methods=['POST'])
def shares_exist():
    path = request.form.get('path')
    if path is not None:
       share = ShareMgt('', path, '')
       exist = share.exist()
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


@app.route("/events", methods=['PUT','POST','GET'])
@basic_auth.required
def events():
    client = request.form.get('client')
    status = request.form.get('status')
    sync_status = request.form.get('sync_status')
    limit = request.form.get('limit')
    if limit is None:
      limit = 50
    events_list = event_form(client, status, sync_status, limit)
    client = ClientMgt("all")
    clientlist = client.list_clients()
    return render_template("events.html", events=events_list, clientlist=clientlist), 200


@app.route("/events/<id>", methods=['GET'])
@basic_auth.required
def event_id(id):
    event = Event(id)
    exist = event.exist()
    if exist:
        event_result = event.info()
        return render_template("event_log.html", event=event_result), 200
    else:
       return render_template("event_404.html", id=int(id)), 404

####  SYNC ENDPOINTS ####


@app.route("/sync/start/<client>", methods=['PUT', 'POST'])
def sync_start(client):
    share = request.form.get('share')
    start_ts = int(request.form.get('start_ts'))
    clientmgt = ClientMgt(client)
    #print("Start Sync")
    if clientmgt.exist()[0] == 0:
      return "Client %s does not exist, register first" % client, 500
    else:
      clientmgt.check_pending()
      clientmgt.start_sync(start_ts, share)
      return "Sync Started, record updated with status %s" % status, 200


@app.route("/sync/end/<client>", methods=['PUT', 'POST'])
def sync_end(client):
    start_ts = int(request.form.get('start_ts'))
    status = request.form.get('status')
    sync_status = request.form.get('sync_status')
    log = request.form.get('log')
    end_ts = int(request.form.get('end_ts'))
    clientmgt = ClientMgt(client)
    #print("End Sync")
    #print("%s : Log Sync Enc Received: %s" % (client, log) )
    if clientmgt.exist()[0] == 0:
      return "Client %s does not exist, register first" % client, 500
    else:
      clientmgt.end_sync(start_ts, end_ts, status, sync_status, log)
      return "Sync Terminated, record updated with status %s" % status, 201

############

#app.run(debug=True,port=8080)
