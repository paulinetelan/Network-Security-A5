import sys, socket, time, threading, re
import logging as log

def establish_protocol(hostname, port, channel, secret):
    sys.stderr.write("Sending IRC protocol messages...\n")
    # IRC server protocol
    # TODO add bot number
    irc.send(bytearray('NICK bot\n', 'utf-8'))
    irc.send(bytearray('USER bot 0 * : bot\n', 'utf-8'))
    irc.send(bytearray('JOIN #' + channel + '\n', 'utf-8'))
    return

def receive_msg():
    sys.stderr.write("Receiving irc messages...\n")
    while True:
        message = irc.recv(2040)
        sys.stderr.write("Message received!\n")
        print(message.decode('utf-8'))

        # message_split[1] = Nickname
        message_split = re.split('!|:', message.decode('utf-8'))
        
        # check for ping-pong message 
        if message_split[0] == 'PING':
            sys.stderr.write("Sending PONG "  + message_split[1] + "\n")
            irc.sendall(bytearray('PONG ' + message_split[1] + '\r\n', 'utf-8'))

        else:
            # actual_message = Message received without escape characters
            actual_message = message_split[3].split()[0]

            # check for secret phrase 
            if (message_split[1] not in controllers) and (actual_message == secret_phrase):
                sys.stderr.write(message_split[1] + " is a Controller!\n")
                controllers.append(message_split[1])
                irc.sendall(bytearray('PRIVMSG '+ message_split[1] + ' :hi from bot \n', 'utf-8'))
            elif message_split[1] in controllers:
                sys.stderr.write("Message from controller\n")
                # TODO handle controller message here
        
    return

# TODO send messages to irc
def send_msg():
    while True:
        message = input()
        sys.stderr.write("Sending message to irc...\n")
        irc.sendall(bytearray(message, 'utf-8'))
    return

if __name__ == '__main__':

    if len(sys.argv) == 5:
        hostname = sys.argv[1]
        port = sys.argv[2]
        channel = sys.argv[3]
        secret_phrase = sys.argv[4]

        # Initialize list of authenticated controllers
        controllers = []

        # Connect to controller
        irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while True:
            try:
                sys.stderr.write("Attempting to connect to server...\n")
                irc.connect((hostname, int(port)))
                # establish irc protocol
                sys.stderr.write("Connected to IRC!\n")
                establish_protocol(hostname, port, channel, secret_phrase)
               
                #start receiving thread
                sys.stderr.write("Starting recv thread...\n")
                receive_thread = threading.Thread(target=receive_msg(), args=())
                receive_thread.daemon = True
                receive_thread.start()

            except socket.error as e:
                sys.stderr.write("{0}\n".format(e))
                sys.stderr.write("Sleeping...\n")
                # If connection fails, sleep for 5s then connect again 
                time.sleep(5)
                continue
    else:
        sys.stderr.write("USAGE: python3 bot.py <hostname> <port> <channel> <secret-phrase>\n")
        sys.exit(1)
