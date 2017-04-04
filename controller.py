import socket
import sys
import irc
import random, string

HOST = ''
PORT = 0000
CHAN = ''
PASS = ''

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

if __name__ == "__main__":
    
    if len(sys.argv) == 5:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        CHAN = sys.argv[3]
        PASS = sys.argv[4]
        NICK = "controller_"+generate_nickname(5)

        s = socket.socket()
        s.connect((HOST, PORT))
        s.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        s.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        s.send("USER c 0 * :{}\r\n".format(NICK).encode("utf-8"))
        s.send("JOIN {}\r\n".format(CHAN).encode("utf-8"))

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
                    NICK = 'controller_'+generate_nickname(5)
                    s.send(("NICK "+NICK+"\r\n").encode('utf-8'))
    
    else:
        print("USAGE: python3 controller.py <hostname> <port> <channel> <secret-phrase>")
        sys.exit(1)