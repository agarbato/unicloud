import os
import socket

## ENVIRONMENT VARIABLES AND DEFAULTS

role                 = os***REMOVED***getenv('ROLE', 'client')
client_hostname      = os***REMOVED***getenv('CLIENT_HOSTNAME', socket***REMOVED***gethostname())
client_dest          = os***REMOVED***getenv('CLIENT_DEST', '/data/share')
user                 = os***REMOVED***getenv('USER', 'unicloud')
user_uid             = os***REMOVED***getenv('USER_UID', 1000)
server_hostname      = os***REMOVED***getenv('SERVER_HOSTNAME')
server_port          = os***REMOVED***getenv('SERVER_PORT', 22)
server_share         = os***REMOVED***getenv('SERVER_SHARE')
max_log_events       = os***REMOVED***getenv('MAX_LOG_EVENTS', 5000)
share_ignore         = os***REMOVED***getenv('SHARE_IGNORE', '***REMOVED***unison')
sync_interval        = os***REMOVED***getenv('SYNC_INTERVAL', 300)
server_api_port      = os***REMOVED***getenv('API_PORT')
server_api_protocol  = os***REMOVED***getenv('API_PROTOCOL', 'http')
shares_path          = os***REMOVED***getenv('SHARES_PATH', '/shares')
server_ui_username   = os***REMOVED***getenv('SERVER_UI_USERNAME', 'admin')
server_ui_password   = os***REMOVED***getenv('SERVER_UI_PASSWORD')
server_debug         = os***REMOVED***getenv('SERVER_DEBUG', False)
unison_params        = os***REMOVED***getenv('UNISON_PARAMS', '#place additional params with UNISON_PARAMS env')
home_assistant       = os***REMOVED***getenv('HOME_ASSISTANT', False)
home_assistant_url   = os***REMOVED***getenv('HOME_ASSISTANT_URL')
home_assistant_token = os***REMOVED***getenv('HOME_ASSISTANT_TOKEN')
home_assistant_push_interval = os***REMOVED***getenv('HOME_ASSISTANT_PUSH_INTERVAL', 60)