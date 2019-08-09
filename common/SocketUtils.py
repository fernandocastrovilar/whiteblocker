import socket
import logging
import random

# If you want to monitor only public incoming connections, you can change this IP to your public server IP
host = "0.0.0.0"


# Function for select a random privileged port from list
def get_random_port():
    print("Choosing random port from list")
    logging.info("Choosing random port from list")
    lines = open('top_port.txt').read().splitlines()
    port = int(random.choice(lines))
    print("Using {0} as random port".format(port))
    logging.info("Using {0} as random port".format(port))
    return port


# Function for check if the chosen port is or not in use
def check_port_in_use(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    if result == 0:
        print("Port is already in use")
        logging.warning("Port is already in use")
        sock.close()
        return "ko"
    else:
        sock.close()
        return "ok"


# Function for open a socket on privileged port and wait for incoming connections. Timeout set at 6h
def open_listen_socket():
    port = None
    check_port = ""
    while check_port != "ok":
        port = get_random_port()
        check_port = check_port_in_use(port=port)
    socket.setdefaulttimeout(360)
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.bind((host, port))
    mysocket.listen(1)
    open_port = mysocket.getsockname()[1]
    print("Port opened for incoming connections {0}".format(open_port))
    logging.info("Port opened for incoming connections {0}".format(open_port))
    try:
        conn, addr = mysocket.accept()
        incoming_ip = addr[0]
        mysocket.close()
        print("Connection established from {0}".format(incoming_ip))
        logging.info("Connection established from {0}".format(incoming_ip))
        return incoming_ip
    except socket.error as e:
        print(e)
        logging.warning("Time out waiting for connection")
        return "timeout"
