import socket
import sys
import irc
import random, string
import threading

QUIT = False
HOST = ''
PORT = 0000
CHAN = ''
PASS = ''
BOTS = []

def privmsg(destination, msg):
    ret = "PRIVMSG "+destination+" :"+msg+"\r\n"
    return ret

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

def recv():
    while not QUIT:
        response = s.recv(1024).decode("utf-8")

        if 'PING' in response:
            print(response)
            msg = response.split(':')
            print('PONG '+msg[1]+'\r\n')
            s.send(('PONG '+msg[1]+'\r\n').encode("utf-8"))

        elif response != '':

            # args[1].strip() = message
            (prefix, command, args)= parsemsg(response)
            sender = prefix.split("!")[0]
            print("Sender: "+sender)
            # debug msgs
            print("prefix: " + prefix)
            print("command: " + command)
            for p in args: print ("arg["+p.strip()+"]")
            print()

            # if nickname already in use
            if command == "433":
                NICK = 'controller_'+generate_nickname(5)
                s.send(("NICK "+NICK+"\r\n").encode('utf-8'))
    return

def send():
    while not QUIT:
        msg = input()
        if msg == "QUIT":
            print("Sending "+(msg+"\r"))
            s.send((msg+"\r\n").encode('utf-8'))
            print("Terminating "+NICK+"...")
            global QUIT 
            QUIT = True
        else:
            print("Sending "+privmsg("#test", msg))
            s.send(privmsg("#test", msg).encode('utf-8'))
    return

if __name__ == "__main__":
    
    if len(sys.argv) == 5:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        CHAN = sys.argv[3]
        PASS = sys.argv[4]
        NICK = "controller_"+generate_nickname(5)

        try:
            s = socket.socket()
            s.connect((HOST, PORT))
            s.send("PASS {}\r\n".format(PASS).encode("utf-8"))
            s.send("NICK {}\r\n".format(NICK).encode("utf-8"))
            s.send("USER c 0 * :{}\r\n".format(NICK).encode("utf-8"))
            s.send("JOIN {}\r\n".format(CHAN).encode("utf-8"))

            recv_thread = threading.Thread(target = recv)
            recv_thread.start()

            send_thread = threading.Thread(target=send)
            send_thread.start()

        except Exception as e:
            print("{0}".format(e))
        finally:
            recv_thread.join()
            send_thread.join()
            sys.exit(1)
    
    else:
        print("USAGE: python3 controller.py <hostname> <port> <channel> <secret-phrase>")
        sys.exit(1)