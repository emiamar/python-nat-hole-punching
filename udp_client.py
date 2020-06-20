import logging
import socket
import sys
from util import *

logger = logging.getLogger()


def main(host='127.0.0.1', port=9999):
    sock = socket.socket(
        # Internet
        socket.AF_INET,
        # UDP
        socket.SOCK_DGRAM
    )
    print(sock)
    sock.sendto(b'0', (host, port))
    while True:
        data, ran_server = sock.recvfrom(1024)
        addr = msg_to_addr(data)
        print(f'Received: Peer {addr} from RS {ran_server}')
        sock.sendto(b'Mac', addr)
        data, addr = sock.recvfrom(1024)
        print(f'Received data from peer {addr}')
        print(f'Data received : {data}')
        return sock, addr


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    main(*addr_from_args(sys.argv))
