# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json
import argparse
import readline

'''Interactive utility to create an xbot++ config.'''

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Interactive utility to create an xbot++ config.')
    parser.add_argument('-f', '--file', metavar='OUTPUT', help='file to write config to, default config.json', default='config.json')
    return parser.parse_args(args)

def line(text):
    print('\n'.join([s.strip() for s in text.split('\n')]))

def main(options=None):
    options = options or parse_args()

    line('''\
    *** xbot++ configuration utility ***
    ''')


    if os.path.exists(options.file):
        print('The file \'%s\' already exists.' % options.file)
        t = input('Overwrite [y/N]? ')
        if t.lower() != 'y':
            raise SystemExit(1)

    newconf = {
        'bot': {},
        'networks': {},
        'modules': {},
    }

    ### newconf['bot'] ###

    line('''
    *** Bot config ***
    Here, we'll set up the general bot config.
    ''')


    while not 'prefix' in newconf['bot']:
        prefix = input('Command prefix to use: ')
        if prefix != '':
            newconf['bot']['prefix'] = prefix
    
    while not 'owner' in newconf['bot']:
        owner = input('Your nickname: ')
        if owner != '':
            newconf['bot']['owner'] = owner

    ### newconf['networks'] ###

    line('''
    *** Network config ***
    ''')

    networks_done = False
    while networks_done == False:
        networkname = False
        while networkname == False:
            networkname = input('Name of the network to connect to: ')
            if networkname == '':
                networkname = False

        newconf['networks'][networkname] = {}

        while not 'protocol' in newconf['networks'][networkname]:
            newconf['networks'][networkname]['protocol'] = input('Protocol of the network you want to connect to: ')
            if newconf['networks'][networkname]['protocol'] == '':
                newconf['networks'][networkname]['protocol'] = False

        while not 'nick' in newconf['networks'][networkname]:
            newconf['networks'][networkname]['nick'] = input('Nickname to use on this network: ')
            if newconf['networks'][networkname]['nick'] == '':
                newconf['networks'][networkname]['nick'] = False

        hosts_done = False
        while hosts_done == False:
            host = input('Server to connect to (use format host:port): ')
            if host != '':
                if 'hosts' in newconf['networks'][networkname]:
                    newconf['networks'][networkname]['hosts'] = ",".join([newconf['networks'][networkname]['hosts'], host])
                else:
                    newconf['networks'][networkname]['hosts'] = host

                if input('Add another server [y/N]? ').lower() != 'y':
                    hosts_done = True

        channels_done = False
        while channels_done == False:
            channel = input('Channel to join to on connect: ')
            if channel != '':
                if 'channels' in newconf['networks'][networkname]:
                    newconf['networks'][networkname]['channels'] = ",".join([newconf['networks'][networkname]['channels'], host])
                else:
                    newconf['networks'][networkname]['channels'] = host

                if input('Add another channel [y/N]? ').lower() != 'y':
                    channels_done = True

        if input('Add another network [y/N]? ').lower() != 'y':
            networks_done = True

    json.dump(newconf, sys.stdout, indent=4, separators=(',', ': '), sort_keys=True)

if __name__ == '__main__':
    main()
