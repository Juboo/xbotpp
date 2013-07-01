# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json
import argparse
from configparser import ConfigParser

'''Utility to migrate a pre-v0.3.x xbot++ config to the new format.'''

def parse_args(args=None):
    '''\
    Parse the command-line arguments for :py:func:`xbotpp.config.migrate.main`.
    '''
    
    parser = argparse.ArgumentParser(description='Utility to migrate a pre-v0.3.x xbot++ config to the new format.')
    parser.add_argument('old_config', metavar='INPUT', 
        help='pre-v0.3.x config file to migrate')
    parser.add_argument('-f', '--file', metavar='OUTPUT', 
        help='file to write migrated config to, default config.json', default='config.json')

    return parser.parse_args(args)

def main(options=None):
    '''\
    Start the migration utility.
    
    `options` is a object with the following attributes:

    * `file`: the name of the file to write the migrated config to (or ``-`` for stdout)
    * `old_config`: the name of the old config file to read and convert.

    This object can be created by the :py:func:`xbotpp.config.migrate.parse_args` function,
    which uses ArgumentParser, or by doing something like the following:

        >>> class Object: pass
        >>> options = Object()
        >>> options.file = 'config.json'
        >>> options.old_config = 'xbotpp.conf'
        >>> xbotpp.config.migrate.main(options)

    This function will return True on success, or raise a SystemExit exception with a 
    numerical error code on an error, which are listed below:

    * 1: Failed while reading the old configuration
    * 2: Failed while converting the configuration
    * 255: Failed while writing the configuration
    '''

    options = options or parse_args()

    oldconf = ConfigParser()
    newconf = {
        'bot': {},
        'networks': {},
        'modules': {
            'load': [],
            'paths': [],
        },
    }

    sys.stderr.write("Reading old configuration... ")
    if oldconf.read(options.old_config):
        print("done.", file=sys.stderr)

    else:
        print("failed :(", file=sys.stderr)
        raise SystemExit(1)

    print("Starting conversion... ", file=sys.stderr)
    try:
        for s in oldconf.sections():
            print(" - %s" % s, file=sys.stderr)
            if s.startswith('network: '):
                y = re.sub('network: ', '', s)
                newconf['networks'][y] = {'protocol': 'irc'}
                for key in oldconf[s]:
                    if key == 'channels' or key == 'hosts':
                        newconf['networks'][y][key] = oldconf[s][key].split(',')
                    else:
                        newconf['networks'][y][key] = oldconf[s][key]
            elif s.startswith('module: '):
                y = re.sub('module: ', '', s)
                newconf['modules']['load'].append(y)
                newconf['modules'][y] = {}
                for key in oldconf[s]:
                    newconf['modules'][y][key] = oldconf[s][key]
            else:
                newconf[s] = {}
                for key in oldconf[s]:
                    newconf[s][key] = oldconf[s][key]
    except:
        print("failed :(", file=sys.stderr)
        print(e, file=sys.stderr)
        raise SystemExit(2)

    sys.stderr.write("Adding module paths... ")

    try:
        newconf['modules']['paths'] = ['./modules']
        print("done.", file=sys.stderr)

    except Exception as e:
        print("failed :(", file=sys.stderr)
        print(e, file=sys.stderr)
        raise SystemExit(2)

    sys.stderr.write("Writing new config... ")

    try:
        if options.file == '-':
            fh = sys.stdout
        else:
            fh = open(options.file, 'w+')

        json.dump(newconf, fh, indent=4, separators=(',', ': '), sort_keys=True)
        print("done.", file=sys.stderr)
        return True

    except Exception as e:
        print("failed :(", file=sys.stderr)
        print(e, file=sys.stderr)
        raise SystemExit(255)

if __name__ == "__main__":
    main()
