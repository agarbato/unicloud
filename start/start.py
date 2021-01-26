import os
import sys
import requests
from time import sleep
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from start_env import *
from shell_cmd import ShellCmd

## LOCAL SETTINGS

root_dir = "/data"
etc_dir = root_dir + "/etc"
log_dir = root_dir + "/log"
ssh_dir = root_dir + "/.ssh"
bin_dir = "/usr/local/bin"
donefile = etc_dir + "/config_done"
authkeyfile = root_dir + "/.ssh/unicloud_authorized_keys"
supervise_cfg = etc_dir + "/supervised.conf"
supervise_log = log_dir + "/supervisord.log"
unison_dir = root_dir + "/.unison"
unison_prf = unison_dir + "/unicloud.prf"
unison_log = log_dir + "/unicloud.log"
server_app_dir = "/usr/local/unicloud"
client_app_dir = "/usr/local/unicloud_client"
client_app_cfg = client_app_dir + "/conf.py"
server_app_cfg = server_app_dir + "/conf.py"
uwsgi_ini = server_app_dir + "/unicloud.ini"

api_url = "%s://%s:%s" % (server_api_protocol, server_hostname, server_api_port)
status_url = api_url + "/status"
client_register_url = api_url + "/clients/register"
share_info_url = api_url + "/shares/info/%s/path" % server_share

role = role.lower()
nl = "\n"

def config_exist():
  if not os.path.exists(donefile):
     return False
  else:
     return True

def api_check():
  maxretry = 3
  delay = 5
  count = 1
  print ("Checking Server API Status")
  while count <= maxretry:
     try:
         response = urlopen(status_url)
     except HTTPError as e:
         exit_screen("api_error", e.code)
     except URLError as e:
         if count == maxretry:
           exit_screen("api_error", e.reason)
         else:
           print("[Retry %d] Fail.. " % count)
           sleep(delay)
           count+=1
     else:
         return("API OK..")

def create_dirs():
  dirs = [etc_dir, log_dir, unison_dir, ssh_dir]
  for dir in dirs:
     if not os.path.exists(dir):
         os.makedirs(dir)
         print ("Creating Dir %s" % dir)

def add_user():
  print ("Adding Unicloud user")
  ShellCmd("groupadd -g %s %s" % ( user_uid, user ))
  ShellCmd("useradd -u %s -g %s -s /bin/bash -c 'unison sync user' -d /data %s" % (user_uid, user_uid, user))
  ShellCmd("chown -R %s:%s %s %s %s %s" % (user, user, ssh_dir, etc_dir, unison_dir, log_dir ))
  ShellCmd("sed -i s/%s:!/%s:*/g /etc/shadow" % (user, user))

def gen_key():
  print ("Generating %s ssh keys" % role)
  if role == "server":
    cmd = ShellCmd("ssh-keygen -A ; mv /etc/ssh /data/")
  else:
    #print (ShellCmd("ls -al /data/"))
    cmd = ShellCmd("su -c \"ssh-keygen -f /data/.ssh/id_rsa -t rsa -N '' \" %s" % user)
    print (cmd)
    ShellCmd("chown -R %s:%s %s" % (user, user, ssh_dir))


def conf_supervisord():
  print ("Creating Supervise Config")
  ## COMMON CONFIG
  with open(supervise_cfg, 'w') as svcfg:
    svcfg.write("[unix_http_server]" + nl)
    svcfg.write("file=/run/supervisord.sock" + nl)
    svcfg.write("[supervisord]" + nl)
    svcfg.write("user=root" + nl)
    svcfg.write("nodaemon=true" + nl)
    svcfg.write("[supervisorctl]" + nl)
    svcfg.write("serverurl=unix:///run/supervisord.sock" + nl)
    svcfg.write("[rpcinterface:supervisor]" + nl)
    svcfg.write("supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface" + nl)
  if role == "server":
     # SERVER CONFIG
     with open(supervise_cfg, 'a') as svcfg:
       svcfg.write("[program:sshd]" + nl)
       #svcfg.write("command = /usr/sbin/sshd -D -f /etc/sshd_config -E /data/log/sshlog" + nl)
       svcfg.write("command = /usr/sbin/sshd -D -f /etc/sshd_config" + nl)
       svcfg.write("redirect_stderr=true" + nl)
       svcfg.write("[program:nginx]" + nl)
       svcfg.write("command=/usr/sbin/nginx -g 'daemon off';" + nl)
       svcfg.write("[program:unicloud_app]" + nl)
       svcfg.write("user=%s" % user + nl)
       svcfg.write("directory=/usr/local/unicloud" + nl)
       svcfg.write("command=/usr/bin/uwsgi --ini %s" % uwsgi_ini + nl)
  else:
     # CLIENT CONFIG
     with open(supervise_cfg, 'a') as svcfg:
       svcfg.write("[program:unicloud]" + nl)
       svcfg.write("user=%s" % user + nl)
       svcfg.write("autorestart=true" + nl)
       svcfg.write("startsec=0" + nl)
       svcfg.write("directory=%s" % client_app_dir + nl)
       svcfg.write("command = python3 main.py" + nl)
       svcfg.write("stdout_logfile = %s/unicloud-supervise-std.log" % log_dir + nl)
       svcfg.write("stdout_logfile_maxbytes=10MB" + nl)
       svcfg.write("stdout_logfile_backups=5" + nl)
       svcfg.write("stderr_logfile = %s/unicloud-supervise-err.log" % log_dir + nl)
       svcfg.write("stderr_logfile_backups=5" + nl)
       svcfg.write("environment=HOME='/data',USER='%s'" % user + nl)

def start_supervisord():
    #print ("Starting Supervisord")
    cmd=ShellCmd("/usr/bin/supervisord --configuration %s --logfile %s" % (supervise_cfg, supervise_log))
    print (cmd.getrc())
    print (cmd)

def test_connection():
    #print ("Checking SSH Connection")
    command="su -c \"ssh -p %s -o \"StrictHostKeyChecking=no\" -o \"BatchMode=yes\" -o \"ConnectTimeout=3\" %s@%s \"echo 2>&1\"\" %s" % (server_port, user, server_hostname, user)
    cmd = ShellCmd(command)
    if cmd.getrc() == 0:
        print ("SSH Connection OK")
        return True
    else:
        print ("SSH Connection KO, exit code %d" % cmd.getrc())
        #print (command)
        #print (cmd)
        return False

def client_conf():
    print ("Exporting environment variables to client app..")
    with open(client_app_cfg, 'w') as cfg:
      cfg.write("client_hostname='%s'" % client_hostname + nl)
      cfg.write("role='%s'" % role + nl)
      cfg.write("user='%s'" % user + nl)
      cfg.write("user_uid='%s'" % user_uid + nl)
      cfg.write("server_hostname='%s'" % server_hostname + nl)
      cfg.write("server_share='%s'" % server_share + nl)
      cfg.write("share_ignore='%s'" % share_ignore + nl)
      cfg.write("unison_params='%s'" % unison_params + nl)
      cfg.write("sync_interval='%s'" % sync_interval + nl)
      cfg.write("server_api_port='%s'" % server_api_port + nl)
      cfg.write("server_api_protocol='%s'" % server_api_protocol + nl)
    print ("Creating unison profile")
    share_path = get_share_path()
    with open(unison_prf, 'w') as cfg:
      cfg.write("root=ssh://%s@%s:%s/%s" % (user, server_hostname, server_port, share_path) + nl)
      cfg.write("root=%s" % client_dest + nl)
      cfg.write("clientHostName=%s" % client_hostname + nl)
      cfg.write("batch = true" + nl)
      cfg.write("auto = true" + nl)
      cfg.write("prefer = newer" + nl)
      cfg.write("log = true" + nl)
      cfg.write("logfile = %s" % unison_log + nl)
      for item in unison_params.split("|"):
          cfg.write("%s" % item + nl)
      for item in share_ignore.split("|"):
        cfg.write("ignore = Name {%s}" % item + nl)

def client_register():
  ssh_keyfile = ssh_dir + "/id_rsa.pub"
  ssh_key = ShellCmd("cat %s" % ssh_keyfile)
  #print (ssh_key)
  print ("Registering client with API, [ %s ]" % client_register_url)
  data = {'name': client_hostname, 'ssh_key': ssh_key, 'share': server_share }
  r = requests.post(url=client_register_url, data=data)

def get_share_path():
   print ("Checking if server share %s exist" % server_share)
   r = requests.get(url=share_info_url)
   if r.status_code == 404:
     exit_screen("share_404")
   else:
     print ("OK %s is defined on server" % server_share)
     return r.text

def server_conf():
     print ("Creating uwsgi app ini..")
     with open(uwsgi_ini, 'w') as cfg:
       cfg.write("[uwsgi]" + nl)
       cfg.write("module = wsgi:app" + nl)
       cfg.write("master = true" + nl)
       cfg.write("processes = 5" + nl)
       cfg.write("enable-threads = true" + nl)
       cfg.write("socket = unicloud.sock" + nl)
       cfg.write("chmod-socket = 664" + nl)
       cfg.write("uid = %d" % user_uid + nl)
       cfg.write("gid = %d" % user_uid + nl)
       cfg.write("vacuum = true" + nl)
       cfg.write("die-on-term = true" + nl)
       cfg.write("log-reopen = true" + nl)
       cfg.write("log-date = [%%Y:%%m:%%d %%H:%%M:%%S]" + nl)
       cfg.write("req-logger = file:/data/log/reqlog" + nl)
       cfg.write("logger = file:/data/log/errlog" + nl)
     print("Exporting environemnt variable to server app")
     with open(server_app_cfg, 'w') as cfg:
       cfg.write("server_ui_username='%s'" % server_ui_username + nl)
       cfg.write("server_ui_password='%s'" % server_ui_password + nl)
       cfg.write("server_debug=%s" % server_debug + nl)
       cfg.write("shares_path='%s'" % shares_path + nl)
       cfg.write("max_log_events='%s'" % max_log_events + nl)
     print ("Set App Permission..")
     ShellCmd("chown -R %s:%s %s" % (user, user, server_app_dir))
     print ("Configure nginx with %s user.." % user)
     ShellCmd("sed -i 's/user nginx;/user %s;/g' /etc/nginx/nginx.conf" % user)
     ShellCmd("sed -i 's/\/var\/log\/nginx\/access.log/\/data\/log\/access.log/g' /etc/nginx/nginx.conf")


def exit_screen(status, error="None"):
    pass
    if status == "client_ok":
      print("========================================================================")
      print("-=(: UniCloud Client started: Enjoy :)=-")
      print("")
      print("User: %s" % user)
      print("Sync server: %s" % server_hostname )
      print("Source: %s" % server_share )
      print("Destination: %s" % client_dest )
      print("========================================================================")
    elif status == "client_ko":
      print("========================================================================")
      print("Connection to Master server %s is not working" % server_hostname )
      print("If this is a new client ACTIVATE first on server UI:")
      print("UI URL : %s" % api_url + "/clients")
      print("%s://%s:%s" % (server_api_protocol, server_hostname, server_api_port))
      print("Exit container now..")
      print("========================================================================")
      sys.exit(255)
    elif status == "server_ok":
      print("========================================================================")
      print("-=(: UniCloud Server started: Enjoy :)=-")
      print("")
      print("SSH : On")
      print("API : On")
      print("Port: %s" % server_port)
      print("User: %s" % user )
      print("========================================================================")
    elif status == "api_error":
      print("========================================================================")
      print("Error contacting API at %s" % status_url)
      print("Error : %s" % error)
      print("Exit container now..")
      print("========================================================================")
      sys.exit(500)
    elif status == "share_404":
      print("========================================================================")
      print("Share %s is not defined on server" % server_share)
      print("Plase define a valid share name")
      print("Exit container now..")
      print("========================================================================")
      sys.exit(404)

############## START ##############

config_status=config_exist()
#print (config_status)

if config_status == False:
  print ("Config not found, first run? Initializing..")
  create_dirs()
  add_user()
  gen_key()
  conf_supervisord()
  ShellCmd("touch %s" % donefile)
  if role == "client":
    print (api_check())
    #print (get_share_path())
    client_register()
else:
  print ("Persistent config found..")
  print ("Initializing environment..")
  add_user()
  conf_supervisord()   # Temporary while understand what's the best supervise option
if role == "client":
  print (api_check())
  #get_share_path()
  #client_register()
  conn = test_connection()
  if conn == True:
     client_conf()
     exit_screen("client_ok")
  else:
     exit_screen("client_ko")
else:
  server_conf()
  exit_screen("server_ok")

start_supervisord()
