# Network-Security-A5

Instructions Jerome:

Things to Install:
- pip install irc

Run Simple IRC Server
- cd to "minircd" (the IRC server to download)
 - run "./miniircd --verbose"
 
Test Connection to IRC
 - run "telnet localhost 6667"
 - then type:
    - nick <name>
    - user <name> 8 * : <more-name>
    
Create a Room
 - *make sure no other room has the same name*
 - join <new-room-name>
 
 Known Commands for IRC Server:
 -join #<room-name>
 -part #<room-name>
 -topic #<room-name> [change-topic]
