# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import socket
import argparse
import readline
import threading
import xbotpp.debug 

'''Example socket client, for user interaction with the dummy protocol.'''

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

def parse_args(args=None):
    '''\
    Parse the command-line arguments for :func:`main`.
    '''

    parser = argparse.ArgumentParser(description='Example socket client, for user interaction with the dummy protocol.')
    parser.add_argument('-f', '--file', metavar='SOCK', help='socket to open', default='xbotpp_dummy_socket')
    parser.add_argument("--debug", action='store_true', help="enable debugging information")
    return parser.parse_args(args)

def recv_thread():
    if client:
        while True:
            data = client.recv(4096)
            if data:
                print(data.strip())
    else:
        xbotpp.debug.write("Socket not there! D:", xbotpp.debug.levels.Error)

def set_debug(e=True):
    '''Enable or disable debugging mode.'''

    debug.print_flagged = e
    debug.write('Debugging information has been %s.' % 'enabled' if e else 'disabled', debug.levels.Info)

def main(options=None):
    '''\
    Start an example socket client.
    '''

    xbotpp.debug.write("Started client.", xbotpp.debug.levels.Info)
    options = options or parse_args()

    if options.debug:
        set_debug(options.debug)

    if os.path.exists(options.file):
        xbotpp.debug.write("Connecting...", xbotpp.debug.levels.Info)
        client.connect(options.file)
        xbotpp.debug.write("Connected.", xbotpp.debug.levels.Info)

        xbotpp.debug.write("Starting socket receive thread.")
        threading.Thread(target=recv_thread).start()
        
        while True:
            x = input("> ")
            if x != "":
                x = "{}\n".format(re.sub('SEP', '\x01', x).strip())
                client.send(x.encode('utf-8'))

    else:
        xbotpp.debug.write("Socket does not exist.", xbotpp.debug.levels.Error)
