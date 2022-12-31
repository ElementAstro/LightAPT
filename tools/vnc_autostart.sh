#!/bin/sh
### BEGIN INIT INFO
# Provides: tightvncserver
# Required-Start: $syslog $remote_fs $network
# Required-Stop: $syslog $remote_fs $network
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Starts VNC Server on system start.
# Description: Starts tight VNC Server. Script written by James Swineson.
### END INIT INFO
# /etc/init.d/tightvncserver
VNCUSER=''
case "$1" in
        start)
                su $VNCUSER -c '/usr/bin/tightvncserver :1'
                echo "Starting TightVNC Server for $VNCUSER"
        ;;
        stop)
                pkill Xtightvnc
                echo "TightVNC Server stopped"
        ;;
        *)
                echo "Usage: /etc/init.d/tightvncserver {start|stop}"
                exit 1
        ;;
esac
exit 0
