import sys, socket, time
import logging as log

def establish_protocol(hostname, port, channel, secret):
    sys.stderr.write("Sending IRC protocol messages...\n")
    # IRC server protocol
    irc.send(bytearray('PASS ' + secret + '\n', 'utf-8'))
    # TODO add bot number
    irc.send(bytearray('NICK bot\n', 'utf-8'))
    irc.send(bytearray('USER bot hostname servname realname\n', 'utf-8'))
    irc.send(bytearray('JOIN ' + channel + '\n', 'utf-8'))
    return

def handle_msg():
    sys.stderr.write("Receiving irc messages...\n")
    while True:
        message = irc.recv(2040)
        sys.stderr.write("Message received!\n")
        print(message.decode('utf-8'))

        if message.find(bytearray('PING', 'utf-8')) != -1:
            irc.send(bytearray('PONG ' + message.split()[1] + '\r\n', 'utf-8'))

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
                # receive irc msgs
                handle_msg()
            except socket.error as e:
                sys.stderr.write("{0}".format(e))
                sys.stderr.write("Sleeping...\n")
                # If connection fails, sleep for 5s then connect again 
                time.sleep(5)
                continue
    else:
        sys.stderr.write("USAGE: python3 bot.py <hostname> <port> <channel> <secret-phrase>\n")
        sys.exit(1)
