# Unicloud, a smart web unison file syncronizer

<img src="***REMOVED***/docs/screenshots/homepage***REMOVED***jpg" width="90%" height="90%"/>

This started as a personal project a while ago until I decided it was stable and "smart" enough to make it public***REMOVED*** I've been using unison for a long time to keep folders in sync between different computers***REMOVED***  I guess I never totally trusted public clouds to host my files***REMOVED***  At first I just added a few cron jobs on my machines and ran unison every n minutes but I felt that in this way I had lost control of it, especially when for some reasons the sync was broken***REMOVED***
I decided to create this project to add a web UI to unison,  monitor all sync and make it simpler to add a new replica of my files***REMOVED***  Add docker to  the recipe, an automatic way to manage your clients  and share your ssh keys and you'll understand the power of this tool :-)
This was one of my first python projects and I have zero to little experience with html, css and graphic design so you might find the result maybe a little old style***REMOVED***  I hope someone is willing to contribute and make it better***REMOVED***

<br><br>

# Features

 - Central API Server to register clients, record logs, manage shares
 - Bi-directional Sync thanks to [Unison](https://www***REMOVED***cis***REMOVED***upenn***REMOVED***edu/~bcpierce/unison/)
 - Log sync events
 - Simple file Manager for shares
 - Sync Threshold warning
 - Small memory usage and image footprint, thanks to [Alpine Linux](https://alpinelinux***REMOVED***org/)

<br><br>

## Quick start

Before you can seriously start using this tools you might want to test locally with docker-compose***REMOVED***
Simply run :

    docker-compose up -d

Docker will build the image and start the project***REMOVED***
Open your browser [here](http://127***REMOVED***0***REMOVED***0***REMOVED***1:5000/) passing credentials specified on the docker-compose file***REMOVED***

Wait a few seconds and the app should be up and running***REMOVED***
On the homepage you will see that there are no registered clients and no shares defined***REMOVED***
The test client will try to register and before you can start to sync you should first activate the client and define the `test1` share name defined on the docker compose through the `SHARE_NAME` env variable***REMOVED***
When you activate a client the ssh pub key will be automatically added to the authorized key and unison will be able to sync using SSH***REMOVED***
Follow the messages and the links on the homepage to complete all the required steps***REMOVED***


<img src="***REMOVED***/docs/screenshots/homepage-events***REMOVED***jpg" width="50%" height="50%"/>


If you want to start again fresh, simple run :

    ***REMOVED***/local_tests/cleanup***REMOVED***sh
    docker-compose up -d

<br><br>

## Environment variables

|Name  |Default  |Scope  | Description
|--|--|--|--|
| TZ |Europe/Rome  |Client/Server|Timezone
| SERVER_UI_USERNAME |admin  |Server|Ui Basic Auth Username
| SERVER_UI_PASSWORD |None  |Server|Ui Basic Auth Password
| SHARES_PATH |/shares  |Server|Server Shares volume
| MAX_LOG_EVENTS |1000  |Server|Max Sync Logs to keep
| CLIENT_HOSTNAME |$HOSTNAME  |Client|Client Hostname (see notes below)
| CLIENT_DEST |/data/share  |Client|Path of synced folder
| SERVER_HOSTNAME |None  |Client|Server Hostname
| SERVER_PORT |22  |Client|Server SSH Port to connect
| SERVER_SHARE |22  |Client|Server Share Name (not path!!)
| API_PROTOCOL |http  |Client|Api protocol: [http\|https]
| API_PORT |80  |Client|Api port
| SHARE_IGNORE |***REMOVED***unison  |Client|Ignore files from share, eg : ***REMOVED***git\|***REMOVED***idea\|***REMOVED***DS_Store
| UNISON_PARAMS |None  |Client|Additional unison profile params eg : owner=false\|perms=0\|dontchmod=true
| SYNC_INTERVAL |300  |Client|Sync Interval seconds
| ROLE |client  |Client/Server|Sync Role: [client\|server]
| USER |unicloud  |Client/Server|Username for running app
| USERID |1000  |Client|Userid for running app

<br><br>


## Volumes and persistence

Client needs two volumes, one to persist its configuration and unison profiles/db files and one for the actual share folder to keep in sync***REMOVED***

 - [**/data**]          Unison and system configuration***REMOVED***
 - [**/data/share**]    Sync volume (can be changed with *CLIENT_DEST* env variable)***REMOVED***

Server also need two volumes:

- [**/data**]          Unison and system configuration***REMOVED***
- [**/shares**]        Shares root folder***REMOVED***

It's best to have a single shares root folder volume and then assign, mount and configure all shares as sub-folders***REMOVED***   
   
\+ [**/shares**]    
&ensp;&ensp;&ensp;[**/shares/share1**]    
&ensp;&ensp;&ensp;[**/shares/share2**]   
   
Shares root folder can be changed with *SHARES_PATH* env variable***REMOVED***   

Nothing prevents you to mount additional volumes on the server and configure them as shares on a different path, just remember to configure correctly *USERID* variable so that the application can read files***REMOVED***   
Shares root is also used by the file manager as root folder so if you mount on a different location you won't be able to browse files***REMOVED***   

<br><br>

## SSH Security

As already described ssh key exchange is done automatically when you activate a client for the first time***REMOVED***   
To add a little bit of security and avoid that a client could actually SSH into the server a restriction is in place to allow only unison command***REMOVED***   

*authorized_keys* file will have this format:      

    command="/usr/bin/unison -server" ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCrNRVWTvt9wLUUXJE6chb8+t24lroL5vOBHAxZ8iIZVrjLm7HOlzX+2kueVQcDkXj+Z44lT6fdvWSG5qksODKzL1LrWRpeJTXGlprjOQE8qobmk68Zh+fWWuPbF5F9pW5856+spfR/ihPzNj9Ih5QM03C0haUHoGfYL+05AnPstSzuhyMOuH/XuH/LNnAQm+Kzg1VJ3l9OUjaQOYvKkQhoQ//bn1ByGmOtQsdqzJBElHJ9nFLkqQLHGTED9sk0TVTe+gifVQVQHz3HXsYM3KyT4VYfznFPcPNJ+SdpyVgdwIwnsa65dWb3uJa/1dIKJ8DHwRrRmwaL0Ck4fkJ5vbvIMtc59cNI11GBEsSUGrxWwcGthH/936l3D3gUnxDVuzgQFMhDJNUewRhk8ttWfn8lY3h/OKyeudlGTFb2Cuy+narK6m4VBYk+mPsdSNxWdchIVxHbXxF//l95JoEp6vm+ZavhKb18DzVbwZ015Gg6O9RneoYnMB9MI0Bxf+/V4/c= unicloud@2078f83040f3 CLIENT:testing-client1***REMOVED***/local_tests/cleanup***REMOVED***sh   
    
To add more security a chroot env could be eventually added in the next future***REMOVED***   
   
     
## Sync Events / Thresholds

### Events
One of the most fancy feature of the app is the events section***REMOVED***   
You can see details about an event id, basically you will see unison log there***REMOVED***   
On the event page you can filter events by different criteria***REMOVED***    
<br>
<img src="***REMOVED***/docs/screenshots/events***REMOVED***jpg" />   
<br>
In order to keep sqlite database small events logs are purged with a daily scheduled tasks***REMOVED***   
Events are not deleted, just  the logs are replaced with a *None* ***REMOVED***   
You can decide how many events logs you want to keep with *MAX_LOG_EVENTS* var,  default is 1000***REMOVED***   
<br>
<img src="***REMOVED***/docs/screenshots/event-detail***REMOVED***jpg" width="70%" height="70%" />   
<br><br>

### Thresholds

In order to have a clear view if a client is in sync you can set a sync threshold (seconds) on client configuration page***REMOVED***   
If you do so, you can check if a client  is *Out of Sync* on the clients page and you will see a message on the homepage warning you that one or more clients are out of sync***REMOVED***      

<br>
<img src="***REMOVED***/docs/screenshots/client-info***REMOVED***jpg"  />
<br><br>

### Simple file manager
A simple file manager provided by [Flask Autoindex](https://flask-autoindex***REMOVED***readthedocs***REMOVED***io/en/latest/) is included in the project   
<br>
<img src="***REMOVED***/docs/screenshots/filemanager***REMOVED***jpg"  />



