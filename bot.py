import sys, socket, time

if __name__ == '__main__':

    if len(sys.argv) == 5:
        hostname = sys.argv[1]
        port = sys.argv[2]
        channel = sys.argv[3]
        secret_phrase = sys.argv[4]

         # Connect to controller
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while True:
            try:
                sock.connect((hostname, int(port)))

                # TODO listen for secret_phrase from Controller
            
            # If connection fails, sleep for 5s then connect again
            except 
                time.sleep(5)
                continue
    else:
        sys.stderr.write("USAGE: python3 bot.py <hostname> <port> <channel> <secret-phrase>\n")
        sys.exit(1)
