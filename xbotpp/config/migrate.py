# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json
import argparse
from configparser import ConfigParser

'''Utility to migrate a pre-v0.3.x xbot++ config to the new format.'''

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Utility to migrate a pre-v0.3.x xbot++ config to the new format.')
    parser.add_argument('old_config', metavar='INPUT', 
        help='pre-v0.3.x config file to migrate')
    parser.add_argument('-f', '--file', metavar='OUTPUT', 
        help='file to write migrated config to, default config.json', default='config.json')

    return parser.parse_args(args)

def main(options=None):
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
        if options.new_config == '-':
            fh = sys.stdout
        else:
            fh = open(options.file, 'w+')

        json.dump(newconf, fh, indent=4, separators=(',', ': '), sort_keys=True)
        print("done.", file=sys.stderr)

    except Exception as e:
        print("failed :(", file=sys.stderr)
        print(e, file=sys.stderr)
        raise SystemExit(3)

if __name__ == "__main__":
    main()
