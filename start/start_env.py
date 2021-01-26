import os
import socket

## ENVIRONMENT VARIABLES AND DEFAULTS

role                 = os.getenv('ROLE', 'client')
client_hostname      = os.getenv('CLIENT_HOSTNAME', socket.gethostname())
client_dest          = os.getenv('CLIENT_DEST', '/data/share')
user                 = os.getenv('USER', 'unicloud')
user_uid             = os.getenv('USER_UID', 1000)
server_hostname      = os.getenv('SERVER_HOSTNAME')
server_port          = os.getenv('SERVER_PORT', 22)
server_share         = os.getenv('SERVER_SHARE')
max_log_events       = os.getenv('MAX_LOG_EVENTS', 5000)
share_ignore         = os.getenv('SHARE_IGNORE', '.unison')
sync_interval        = os.getenv('SYNC_INTERVAL', 300)
server_api_port      = os.getenv('API_PORT')
server_api_protocol  = os.getenv('API_PROTOCOL', 'http')
shares_path          = os.getenv('SHARES_PATH', '/shares')
server_ui_username   = os.getenv('SERVER_UI_USERNAME', 'admin')
server_ui_password   = os.getenv('SERVER_UI_PASSWORD')
server_debug         = os.getenv('SERVER_DEBUG', False)
unison_params        = os.getenv('UNISON_PARAMS', '#place additional params with UNISON_PARAMS env')
