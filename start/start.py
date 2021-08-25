import os
import sys
import requests
import socket
from time import sleep
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from start_env import *
from shell_cmd import ShellCmd

## LOCAL SETTINGS

root_dir = "/data"
etc_dir = f"{root_dir}/etc"
log_dir = f"{root_dir}/log"
ssh_dir = f"{root_dir}/.ssh"
bin_dir = "/usr/local/bin"
donefile = f"{etc_dir}/config_done"
authkeyfile = f"{root_dir}/.ssh/unicloud_authorized_keys"
supervise_cfg = f"{etc_dir}/supervised.conf"
supervise_log = f"{log_dir}/supervisord.log"
unison_dir = f"{root_dir}/.unison"
unison_prf = f"{unison_dir}/unicloud.prf"
unison_log = f"{log_dir}/unicloud.log"
server_app_dir = "/usr/local/unicloud"
client_app_dir = "/usr/local/unicloud_client"
client_app_cfg = f"{client_app_dir}/conf.py"
server_app_cfg = f"{server_app_dir}/conf.py"
uwsgi_ini = f"{server_app_dir}/unicloud.ini"

api_url = f"{server_api_protocol}://{server_hostname}:{server_api_port}"
status_url = f"{api_url}/status"
client_register_url = f"{api_url}/clients/register"
share_info_url = f"{api_url}/shares/info/{server_share}/path"

user_uid = int(user_uid)

role = role.lower()


def config_exist():
  if not os.path.exists(donefile):
     return False
  else:
     return True


def api_check():
  maxretry = 3
  delay = 5
  count = 1
  print("Checking Server API Status")
  while count <= maxretry:
     try:
         urlopen(status_url)
     except HTTPError as e:
         exit_screen("api_error", e.code)
     except URLError as e:
         if count == maxretry:
           exit_screen("api_error", e.reason)
         else:
           print(f"[Retry {count}] Fail.. ")
           sleep(delay)
           count += 1
     else:
         return "API OK.."


def create_dirs():
  dirs = [etc_dir, log_dir, unison_dir, ssh_dir]
  for dir in dirs:
     if not os.path.exists(dir):
         os.makedirs(dir)
         print(f"Creating Dir {dir}")


def add_user():
  print("Adding Unicloud user")
  ShellCmd(f"groupadd -g {user_uid} {user}")
  ShellCmd(f"useradd -u {user_uid} -g {user_uid} -s /bin/bash -c 'unison sync user' -d /data {user}")
  ShellCmd(f"chown -R {user}:{user} {ssh_dir} {etc_dir} {unison_dir} {log_dir}")
  ShellCmd(f"sed -i s/{user}:!/{user}:*/g /etc/shadow")
  if user_gids:
    print(f"Adding user to groups {user_gids}")
    cmd = ShellCmd(f"usermod -a -G {user_gids} {user}")
    print(cmd)


def gen_key():
  print(f"Generating {role} ssh keys")
  if role == "server":
    ShellCmd("ssh-keygen -A ; mv /etc/ssh /data/")
    # fix possible wrong permission on home folder that prevents ssh to work properly
    ShellCmd("chmod g-w /data")
  else:
    cmd = ShellCmd(f"su -c \"ssh-keygen -f /data/.ssh/id_rsa -t rsa -N '' \" {user}")
    print(cmd)
    ShellCmd(f"chown -R {user}:{user} {ssh_dir}")


def conf_supervisord():
  print("Creating Supervise Config")
  ## COMMON CONFIG
  with open(supervise_cfg, 'w') as svcfg:
    svcfg.write("[unix_http_server]\n")
    svcfg.write("file=/run/supervisord.sock\n")
    svcfg.write("[supervisord]\n")
    svcfg.write("user=root\n")
    svcfg.write("nodaemon=true\n")
    svcfg.write("[supervisorctl]\n")
    svcfg.write("serverurl=unix:///run/supervisord.sock\n")
    svcfg.write("[rpcinterface:supervisor]\n")
    svcfg.write("supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface\n")
  if role == "server":
     # SERVER CONFIG
     with open(supervise_cfg, 'a') as svcfg:
       svcfg.write("[program:sshd]\n")
       #SSH DEBUG
       #svcfg.write("command = /usr/sbin/sshd -D -f /etc/sshd_config -E /data/log/sshlog" + nl)
       svcfg.write("command = /usr/sbin/sshd -D -f /etc/sshd_config\n")
       svcfg.write("redirect_stderr=true\n")
       svcfg.write("[program:nginx]\n")
       svcfg.write("command=/usr/sbin/nginx -g 'daemon off';\n")
       svcfg.write("[program:unicloud_app]\n")
       svcfg.write(f"user={user}\n")
       svcfg.write("directory=/usr/local/unicloud\n")
       svcfg.write(f"command=/usr/bin/uwsgi --ini {uwsgi_ini}\n")
  else:
     # CLIENT CONFIG
     with open(supervise_cfg, 'a') as svcfg:
       svcfg.write("[program:unicloud]\n")
       svcfg.write(f"user={user}\n")
       svcfg.write("autorestart=true\n")
       svcfg.write("startsec=0\n")
       svcfg.write(f"directory={client_app_dir}\n")
       svcfg.write("command = python3 main.py\n")
       svcfg.write(f"stdout_logfile = {log_dir}/unicloud-supervise-std.log\n")
       svcfg.write("stdout_logfile_maxbytes=10MB\n")
       svcfg.write("stdout_logfile_backups=5\n")
       svcfg.write(f"stderr_logfile = {log_dir}/unicloud-supervise-err.log\n")
       svcfg.write("stderr_logfile_backups=5\n")
       svcfg.write(f"environment=HOME='/data',USER='{user}'\n")


def start_supervisord():
    #print ("Starting Supervisord")
    cmd = ShellCmd(f"/usr/bin/supervisord --configuration {supervise_cfg} --logfile {supervise_log}")
    print(cmd.getrc())
    print(cmd)


def cache_api_hostname():
    ip_address = socket.gethostbyname(server_hostname)
    with open("/etc/hosts", 'a') as etc_hosts:
        etc_hosts.write(f"{ip_address}   {server_hostname}\n")


def test_connection():
    #print ("Checking SSH Connection")
    command = f"su -c \"ssh -p {server_port} -o \"StrictHostKeyChecking=no\" -o \"BatchMode=yes\" -o \"ConnectTimeout=3\" {user}@{server_hostname} \"echo 2>&1\"\" {user}"
    cmd = ShellCmd(command)
    if cmd.getrc() == 0:
        print("SSH Connection OK")
        return True
    else:
        print(f"SSH Connection KO, exit code {cmd.getrc()}")
        return False


def client_conf():
    print("Exporting environment variables to client app..")
    with open(client_app_cfg, 'w') as cfg:
      cfg.write(f"client_hostname='{client_hostname}'\n")
      cfg.write(f"role='{role}'\n")
      cfg.write(f"user='{user}'\n")
      cfg.write(f"user_uid='{user_uid}'\n")
      cfg.write(f"server_hostname='{server_hostname}'\n")
      cfg.write(f"server_share='{server_share}'\n")
      cfg.write(f"share_ignore='{share_ignore}'\n")
      cfg.write(f"unison_params='{unison_params}'\n")
      cfg.write(f"sync_interval='{sync_interval}'\n")
      cfg.write(f"server_api_port='{server_api_port}'\n")
      cfg.write(f"server_api_protocol='{server_api_protocol}'\n")
    print("Creating unison profile")
    share_path = get_share_path()
    with open(unison_prf, 'w') as cfg
      cfg.write(f"root=ssh://{user}@{server_hostname}:{server_port}/{share_path}\n")
      cfg.write(f"root={client_dest}\n")
      cfg.write(f"clientHostName={client_hostname}\n")
      cfg.write("batch = true\n")
      cfg.write("auto = true\n")
      cfg.write("prefer = newer\n")
      cfg.write("log = true\n")
      cfg.write(f"logfile = {unison_log}\n")
      for item in unison_params.split("|"):
          cfg.write(f"{item}\n")
      for item in share_ignore.split("|"):
        cfg.write(f"ignore = Name {item}\n")


def client_register():
  ssh_keyfile = f"{ssh_dir}/id_rsa.pub"
  ssh_key = ShellCmd(f"cat {ssh_keyfile}")
  print(f"Registering client with API, [ {client_register_url} ]")
  data = {'name': client_hostname, 'ssh_key': ssh_key, 'share': server_share }
  requests.post(url=client_register_url, data=data)


def get_share_path():
   print(f"Checking if server share {server_share} exist")
   r = requests.get(url=share_info_url)
   if r.status_code == 404:
     exit_screen("share_404")
   else:
     print(f"OK {server_share} is defined on server")
     return r.text


def server_conf():
     print("Creating uwsgi app ini..")
     with open(uwsgi_ini, 'w') as cfg:
       cfg.write("[uwsgi]\n")
       cfg.write("module = wsgi:app\n")
       cfg.write("master = true\n")
       cfg.write("processes = 5\n")
       cfg.write("enable-threads = true\n")
       cfg.write("socket = unicloud.sock\n")
       cfg.write("chmod-socket = 664\n")
       cfg.write(f"uid = {user_uid}\n")
       cfg.write(f"gid = {user_uid}\n")
       cfg.write("vacuum = true\n")
       cfg.write("die-on-term = true\n")
       cfg.write("log-reopen = true\n")
       cfg.write("log-date = [%%Y:%%m:%%d %%H:%%M:%%S]\n")
       cfg.write("req-logger = file:/data/log/reqlog\n")
       cfg.write("logger = file:/data/log/errlog\n")
     print("Exporting environment variable to server app")
     with open(server_app_cfg, 'w') as cfg:
       cfg.write(f"server_ui_username='{server_ui_username}'\n")
       cfg.write(f"server_ui_password='{server_ui_password}'\n")
       cfg.write(f"server_debug={server_debug}\n")
       cfg.write(f"shares_path='{shares_path}'\n")
       cfg.write(f"max_log_events='{max_log_events}'\n")
       cfg.write(f"home_assistant={home_assistant}\n")
       cfg.write(f"home_assistant_url='{home_assistant_url}'\n")
       cfg.write(f"home_assistant_token='{home_assistant_token}'\n")
       cfg.write(f"home_assistant_push_interval={int(home_assistant_push_interval)}")
     print("Set App Permission..")
     ShellCmd(f"chown -R {user}:{user} {server_app_dir}")
     print(f"Configure nginx with {user} user..")
     ShellCmd(f"sed -i 's/user nginx;/user {user};/g' /etc/nginx/nginx.conf")
     ShellCmd(f"sed -i 's/\/var\/log\/nginx\/access.log/\/data\/log\/access.log/g' /etc/nginx/nginx.conf")


def exit_screen(status, error="None"):
    pass
    if status == "client_ok":
      print("========================================================================")
      print("-=(: UniCloud Client started: Enjoy :)=-")
      print("")
      print(f"User: {user}")
      print(f"Sync server: {server_hostname}")
      print(f"Source: {server_share}")
      print(f"Destination: {client_dest}")
      print("========================================================================")
    elif status == "client_ko":
      print("========================================================================")
      print(f"Connection to Master server {server_hostname} is not working")
      print("If this is a new client ACTIVATE first on server UI:")
      print(f"UI URL : {api_url}/clients")
      print(f"{server_api_protocol}://{server_hostname}:{server_api_port}")
      print("Exit container now..")
      print("========================================================================")
      sys.exit(255)
    elif status == "server_ok":
      print("========================================================================")
      print("-=(: UniCloud Server started: Enjoy :)=-")
      print("")
      print("SSH : On")
      print("API : On")
      print(f"Port: {server_port}")
      print(f"User: {user}")
      print("========================================================================")
    elif status == "api_error":
      print("========================================================================")
      print(f"Error contacting API at {status_url}")
      print(f"Error : {error}")
      print("Exit container now..")
      print("========================================================================")
      sys.exit(500)
    elif status == "share_404":
      print("========================================================================")
      print(f"Share {server_share} is not defined on server")
      print("Plase define a valid share name")
      print("Exit container now..")
      print("========================================================================")
      sys.exit(404)

############## START ##############


config_status = config_exist()


if not config_status:
  print("Config not found, first run? Initializing..")
  create_dirs()
  add_user()
  gen_key()
  conf_supervisord()
  ShellCmd(f"touch {donefile}")
  if role == "client":
    print(api_check())
    #print (get_share_path())
    client_register()
else:
  print("Persistent config found..")
  print("Initializing environment..")
  add_user()
  conf_supervisord()
if role == "client":
  cache_api_hostname()
  print(api_check())
  #get_share_path()
  #client_register()
  conn = test_connection()
  if conn:
     client_conf()
     exit_screen("client_ok")
  else:
     exit_screen("client_ko")
else:
  server_conf()
  exit_screen("server_ok")

start_supervisord()
