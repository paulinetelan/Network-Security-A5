import re
def port(number):
    port = int(number)

    if(port < 65536 and port > -1):
        return True
    else:
        return False
    

# http://stackoverflow.com/questions/2532053/validate-a-hostname-string
def hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))