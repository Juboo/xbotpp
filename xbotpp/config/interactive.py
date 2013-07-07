# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json
import argparse
try:
    import readline
except:
    print("!! Failed to import readline, you may not be able to use the arrow keys when editing.")

'''Interactive utility to create an xbot++ config.'''

def parse_args(args=None):
    '''\
    Parse the command-line arguments for :py:func:`xbotpp.config.interactive.main`.
    '''

    parser = argparse.ArgumentParser(description='Interactive utility to create an xbot++ config.')
    parser.add_argument('-f', '--file', metavar='OUTPUT', help='file to write config to, default config.json', default='config.json')
    return parser.parse_args(args)

def line(text):
    '''\
       >>> print('\\n'.join[s.strip() for s in text.split('\\n')]))

    '''

    print('\n'.join([s.strip() for s in text.split('\n')]))

def main(options=None):
    '''\
    Start the interactive configuration utility.
    
    `options` is a object with the attribute `file`, containing the name
    of the file to write to (or ``-`` for stdout). This can be created by
    the :py:func:`xbotpp.config.interactive.parse_args` function.
    '''

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
        'modules': {
            'load': [],
            'paths': [],
        },
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

        newconf['networks'][networkname]['servers'] = []
        hosts_done = False
        while hosts_done == False:
            host = input('Server to connect to (use format host:port): ')
            if host != '':
                newconf['networks'][networkname]['servers'].append(host)

                if input('Add another server [y/N]? ').lower() != 'y':
                    hosts_done = True

        newconf['networks'][networkname]['channels'] = []
        channels_done = False
        while channels_done == False:
            channel = input('Channel to join to on connect: ')
            if channel != '':
                newconf['networks'][networkname]['channels'].append(channel)

                if input('Add another channel [y/N]? ').lower() != 'y':
                    channels_done = True

        if input('Add another network [y/N]? ').lower() != 'y':
            networks_done = True

    line('''
    *** Module config ***
    ''')

    paths_done = False

    line('''
    Now we'll have to add paths to search for modules.
    You may want to add a path in the current directory, as well as the system module path.
    ''')

    while paths_done == False:
        path = input('Path to search for modules: ')
        if path != '':
            newconf['modules']['paths'].append(path)

            if input('Add another path [y/N]? ').lower() != 'y':
                paths_done = True

    modules_done = False
    while modules_done == False:
        module = input('Name of module to load on startup: ')
        if module != '':
            newconf['modules']['load'].append(module)

            if input('Add another module [y/N]? ').lower() != 'y':
                modules_done = True

    line('''
    *** Configuration complete ***
    ''')

    if input('Write config to %s [Y/n]? ' % ('file \'{0}\''.format(options.file) if options.file != '-' else 'stdout')).lower() == 'y':
        if options.file == '-':
            fh = sys.stdout
        else:
            fh = open(options.file, 'w+')

        json.dump(newconf, fh, indent=4, separators=(',', ': '), sort_keys=True)
        raise SystemExit(0)

    print('Exiting without saving config.')


if __name__ == '__main__':
    main()
