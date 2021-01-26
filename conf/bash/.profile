# ~/***REMOVED***profile: executed by the command interpreter for login shells***REMOVED***
# This file is not read by bash(1), if ~/***REMOVED***bash_profile or ~/***REMOVED***bash_login
# exists***REMOVED***
# see /usr/share/doc/bash/examples/startup-files for examples***REMOVED***
# the files are located in the bash-doc package***REMOVED***

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package***REMOVED***
#umask 022

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include ***REMOVED***bashrc if it exists
    if [ -f "$HOME/***REMOVED***bashrc" ]; then
	***REMOVED*** "$HOME/***REMOVED***bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi
