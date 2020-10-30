#!/usr/bin/env python
# import sys

import logging
import socket
# import struct
from concurrent import futures

from threading import Event, Thread
from util import *

# sock = ''
# connection = ''
# addr = ''

logger = logging.getLogger('client')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
STOP = Event()


def accept(port):
    global connection
    global addr
    logger.info("accept %s", port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('', port))
    s.listen(1)
    s.settimeout(5)
    while not STOP.is_set():
        try:
            connection, addr = s.accept()
            logger.info(
                "First accepted the connection {}, addr {}".format(connection, addr))
            STOP.set()
        except socket.timeout:
            continue
        else:
            logger.info("Accepted success! %s", addr)
            STOP.set()


def connect(local_addr, addr):
    logger.info("connect from %s to %s", local_addr, addr)
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(local_addr)
    sock.settimeout(5)
    while not STOP.is_set():
        try:
            sock.connect(addr)
            print("Sucessful connecting {} -- {}".format(local_addr, addr))
        except socket.error:
            continue
        # except Exception as exc:
        #     logger.exception("unexpected exception encountered")
        #     break
        else:
            logger.info("connected from %s to %s success!", local_addr, addr)
            STOP.set()


def main(host='45.33.117.94', port=5005):
    sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sa.connect((host, port))
    priv_addr = sa.getsockname()

    send_msg(sa, addr_to_msg(priv_addr))
    data = recv_msg(sa)
    logger.info("client %s %s - received data: %s", priv_addr[0], priv_addr[1], data)
    pub_addr = msg_to_addr(data)
    send_msg(sa, addr_to_msg(pub_addr))

    data = recv_msg(sa)
    pubdata, privdata = data.split(b'|')
    client_pub_addr = msg_to_addr(pubdata)
    client_priv_addr = msg_to_addr(privdata)
    logger.info(
        "client public is %s and private is %s, peer public is %s private is %s",
        pub_addr, priv_addr, client_pub_addr, client_priv_addr,
    )

    threads = {
        '0_accept': Thread(target=accept, args=(client_pub_addr[1],)),
        '1_accept': Thread(target=accept, args=(priv_addr[1],)),
        '2_connect': Thread(target=connect, args=(priv_addr, client_pub_addr,)),
        # '3_connect': Thread(target=connect, args=(priv_addr, client_priv_addr,)),
    }
    # for name in sorted(threads.keys()):
    #     logger.info('start thread %s', name)
    #     threads[name].start()
    # while threads:
    #     keys = list(threads.keys())
    #     for name in keys:
    #         try:
    #             threads[name].join(1)
    #         except TimeoutError:
    #             continue
    #         if not threads[name].is_alive():
    #             threads.pop(name)
    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(accept, (client_pub_addr[1],))
        executor.submit(accept, (priv_addr[1],))
        executor.submit(connect, (priv_addr, client_pub_addr,))
        executor.submit(connect, (priv_addr, client_priv_addr,))
    if connection and addr:
        return connection
    if sock:
        return sock


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, message='%(asctime)s %(message)s')
    main()
