import sys, socket, time, threading
import logging as log

def establish_protocol(hostname, port, channel, secret):
    sys.stderr.write("Sending IRC protocol messages...\n")
    # IRC server protocol
    
    # jerome: assume theres no secret
    #irc.send(bytearray('PASS ' + secret + '\n', 'utf-8'))
    
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

        if message.find(bytearray('PING', 'utf-8')) != -1:
            print('PONG'  + message.split()[1])
            irc.send(bytearray('PONG ' + message.split()[1] + '\r\n', 'utf-8'))

    return

# TODO send messages to irc
def send_msg():
    return

if __name__ == '__main__':

    if len(sys.argv) == 5:
        hostname = sys.argv[1]
        port = sys.argv[2]
        channel = sys.argv[3]
        secret_phrase = sys.argv[4]

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
                receive_thread = threading.Thread(target=receive_msg(), args=())
                receive_thread.daemon = True
                receive_thread.start()

            except socket.error as e:
                sys.stderr.write("Sleeping...\n")
                # If connection fails, sleep for 5s then connect again 
                time.sleep(5)
                continue
    else:
        sys.stderr.write("USAGE: python3 bot.py <hostname> <port> <channel> <secret-phrase>\n")
        sys.exit(1)