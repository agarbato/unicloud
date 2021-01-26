# ~/***REMOVED***bashrc: executed by bash(1) for non-login shells***REMOVED***
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# don't put duplicate lines in the history***REMOVED*** See bash(1) for more options
# ***REMOVED******REMOVED******REMOVED*** or force ignoredups and ignorespace
HISTCONTROL=ignoredups:ignorespace

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=10000
HISTFILESIZE=10000
export EDITOR='vim'

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS***REMOVED***
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429)***REMOVED*** (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf***REMOVED***)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/***REMOVED***dircolors && eval "$(dircolors -b ~/***REMOVED***dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'
    alias keyon='unset SSH_ASKPASS ; ssh-add -t 57600'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
    alias giga='ssh giga'
    alias linode='ssh -p 2222 root@linode'
    alias vi='vim***REMOVED***tiny'
    alias vim='vim***REMOVED***tiny'
    alias unilog='tail -f /var/log/unison***REMOVED***log'
    alias rmlock='rm ~/***REMOVED***unison/unison***REMOVED***lock'
    alias wlanadjust='/home/andrea/bin/wlanadjust'
    alias cloudsync='/home/andrea/bin/giga-cloud***REMOVED***sh default'
    alias musicsync='unison -perms=0 music'
    alias musicsync2usb='unison -perms=0 music2usb'
    alias cloudpvtmnt='touch /home/andrea/***REMOVED***unison/unison***REMOVED***lock ; sudo mount -t ecryptfs /home/andrea/cloud/Documents/personalenc /home/andrea/cloud/Documents/personalenc -o ecryptfs_fnek_sig=ef97c90312c0c81a,key=passphrase,ecryptfs_cipher=aes,ecryptfs_key_bytes=16,ecryptfs_passthrough=no,ecryptfs_enable_filename_crypto=yes'
    alias cloudpvtumnt='rm /home/andrea/***REMOVED***unison/unison***REMOVED***lock ; sudo umount /home/andrea/cloud/Documents/personalenc'
    alias slideshow='feh -rdz -D 5 *'

fi

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias vi='vim'

# Alias definitions***REMOVED***
# You may want to put all your additions into a separate file like
# ~/***REMOVED***bash_aliases, instead of adding them here directly***REMOVED***
# See /usr/share/doc/bash-doc/examples in the bash-doc package***REMOVED***

if [ -f ~/***REMOVED***bash_aliases ]; then
    ***REMOVED*** ~/***REMOVED***bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash***REMOVED***bashrc and /etc/profile
# sources /etc/bash***REMOVED***bashrc)***REMOVED***
if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
    ***REMOVED*** /etc/bash_completion
fi

export PATH=$PATH:/sbin:/home/andrea/bin

unset HISTFILE
