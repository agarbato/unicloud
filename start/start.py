import os
import stat
import sys
import requests
import socket
from time import sleep
from jinja2 import Environment, FileSystemLoader
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from start_env import *
from shell_cmd import ShellCmd

## LOCAL SETTINGS

root_dir = "/data"
etc_dir = f"{root_dir}/etc"
log_dir = f"{root_dir}/log"
ssh_dir = f"{root_dir}/.ssh"
backup_dir = f"{root_dir}/{shares_path}/unicloud-backup"
backup_cron_file = "/etc/periodic/daily/unicloud-backup"
bin_dir = "/usr/local/bin"
donefile = f"{etc_dir}/config_done"
authkeyfile = f"{root_dir}/.ssh/unicloud_authorized_keys"
supervise_cfg = f"{etc_dir}/supervised.conf"
supervise_log = f"{log_dir}/supervisord.log"
unison_dir = f"{root_dir}/.unison"
unison_prf = f"{unison_dir}/unicloud.prf"
unison_replica_ssh_prf = f"{unison_dir}/unicloud_replica_ssh_keys.prf"
unison_log = f"{log_dir}/unicloud.log"
server_app_dir = "/usr/local/unicloud"
client_app_dir = "/usr/local/unicloud_client"
client_app_cfg = f"{client_app_dir}/conf.py"
server_app_cfg = f"{server_app_dir}/conf.py"
uwsgi_ini = f"{server_app_dir}/unicloud.ini"

api_url = f"{server_api_protocol}://{server_api_hostname}:{server_api_port}"
status_url = f"{api_url}/status"
client_register_url = f"{api_url}/clients/register"
share_info_url = f"{api_url}/shares/info/{server_share}/path"

user_uid = int(user_uid)
role = role.lower()
env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True, lstrip_blocks=True)


def config_exist():
  if not os.path.exists(donefile):
     return False
  else:
     return True


def render_template(template_filename, context):
    return env.get_template(template_filename).render(context)


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
  dirs = [etc_dir, log_dir, unison_dir, ssh_dir, shares_path, backup_dir]
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
  if role == "server" or role == "replica_server":
    ShellCmd("ssh-keygen -A ; mv /etc/ssh /data/")
    # fix possible wrong permission on home folder that prevents ssh to work properly
    ShellCmd("chmod g-w /data")
  if role == "client" or role == "replica_server":
    cmd = ShellCmd(f"su -c \"ssh-keygen -f /data/.ssh/id_rsa -t rsa -N '' \" {user}")
    print(cmd)
    ShellCmd(f"chown -R {user}:{user} {ssh_dir}")


def conf_supervisord():
  print("Creating Supervise Config")
  context = {
      'role': role,
      'log_dir': log_dir,
      'uwsgi_ini': uwsgi_ini,
      'user': user,
      'client_app_dir': client_app_dir
  }  
  with open(supervise_cfg, "w") as f:
    file = render_template('supervised.tpl.conf', context)
    f.write(file)


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
        print(f"SSH Connection KO, exit code {cmd.getrc()}, output {cmd}")
        return cmd


def client_conf(role):
    print("Exporting environment variables to client app..")
    context = {
        'client_hostname': client_hostname,
        'role': role,
        'user': user,
        'user_uid': user_uid,
        'server_hostname': server_hostname,
        'server_share': server_share,
        'share_ignore': share_ignore,
        'unison_params': unison_params,
        'sync_interval': sync_interval,
        'server_api_hostname': server_api_hostname,
        'server_api_port': server_api_port,
        'server_api_protocol': server_api_protocol
    }
    with open(client_app_cfg, 'w') as f:
      file = render_template('clientconf.tpl.py', context)
      f.write(file)
    print("Creating unison profile")
    share_path = get_share_path()
    context = {
        'user': user,
        'server_hostname': server_hostname,
        'server_port': server_port,
        'share_path': share_path,
        'client_hostname': client_hostname,
        'client_dest': client_dest,
        'unison_params': unison_params,
        'share_ignore': share_ignore,
    }
    with open(unison_prf, 'w') as f:
      file = render_template('unicloud.tpl.prf', context)
      f.write(file)
    if role == "replica_server":
        context = {
            'user': user,
            'server_hostname': server_hostname,
            'server_port': server_port,
            'client_hostname': client_hostname
        }
        with open(unison_replica_ssh_prf, 'w') as f:
            file = render_template('unicloud-authkey.tpl.prf', context)
            f.write(file)


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
     if server_api_hostname != server_hostname:
        return replica_server_source
     else:
        return r.text


def server_conf():
     print("Creating uwsgi app ini..")
     context = {'user_uid': user_uid}
     with open(uwsgi_ini, 'w') as f:
       file = render_template('unicloud.tpl.ini', context)
       f.write(file)

     print("Exporting environment variable to server app")
     context = {
         'server_ui_username': server_ui_username,
         'server_ui_password': server_ui_password,
         'server_debug': server_debug,
         'shares_path': shares_path,
         'max_log_events': max_log_events,
         'home_assistant': home_assistant,
         'home_assistant_url': home_assistant_url,
         'home_assistant_token': home_assistant_token,
         'home_assistant_push_interval': int(home_assistant_push_interval)
     }
     with open(server_app_cfg, 'w') as f:
       file = render_template('serverconf.tpl.py', context)
       f.write(file)

     print("Configure Autobackup Cron..")
     context = {'shares_path': shares_path}
     with open(backup_cron_file, 'w') as f:
         file = render_template('unicloud-backup.tpl', context)
         f.write(file)

     st = os.stat(backup_cron_file)
     os.chmod(backup_cron_file, st.st_mode | stat.S_IEXEC)
     print("Set App Permission..")
     ShellCmd(f"chown -R {user}:{user} {server_app_dir}")
     print(f"Configure nginx with {user} user..")
     ShellCmd(f"sed -i 's/user nginx;/user {user};/g' /etc/nginx/nginx.conf")
     ShellCmd(f"sed -i 's/\/var\/log\/nginx\/access.log/\/data\/log\/access.log/g' /etc/nginx/nginx.conf")


def exit_screen(status, error="None", role="None"):
    pass
    if status == "client_ok":
      print("========================================================================")
      if role == "client":
        print("-=(: UniCloud Client started: Enjoy :)=-")
      elif role == "replica_server":
        print("-=(: UniCloud Client [REPLICA SERVER] started: Enjoy :)=-")
        print("")
        print("SSH : On")
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
      print(f"{server_api_protocol}://{server_api_hostname}:{server_api_port}")
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
  if role == "client" or role == "replica_server":
    print(api_check())
    #print (get_share_path())
    client_register()
else:
  print("Persistent config found..")
  print("Initializing environment..")
  add_user()
  conf_supervisord()
if role == "client" or role == "replica_server":
  cache_api_hostname()
  print(api_check())
  #get_share_path()
  #client_register()
  conn = test_connection()
  if conn:
     client_conf(role)
     exit_screen("client_ok", "None", role)
  else:
     exit_screen("client_ko")
else:
  server_conf()
  exit_screen("server_ok")

start_supervisord()
