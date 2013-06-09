# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json
import inspect
import argparse
from xbotpp import debug
from xbotpp import handler
from xbotpp import modules
from xbotpp import protocol


__version__ = 'v0.3.0'
config = {}
state = {}

def parse_args(args=None):
    '''Parse the arguments to the bot.'''

    parser = argparse.ArgumentParser(usage='xbotpp [options]')
    parser.add_argument('-c', '--config', metavar='FILE', help='read configuration from FILE', default='config.json')
    parser.add_argument('-n', '--network', metavar='NETWORK', help='connect to the network named NETWORK')
    parser.add_argument("--debug", action='store_true', help="enable debugging information")
    return parser.parse_args(args)

def main():
    '''Command-line entry point.'''

    options = parse_args()
    if options.debug:
        set_debug()

    init(options)

def set_debug(e=True):
    '''Enable or disable debugging mode.'''

    debug.print_flagged = e
    debug.write('Debugging information has been %s.' % 'enabled' if e else 'disabled', debug.levels.Info)

def init(options):
    '''Initialize the bot and load our configuration.'''

    debug.write('Entered init().')

    if os.path.exists(options.config):
        try:
            global config
            config = json.load(open(options.config, 'r'))

            if not 'networks' in config:
                debug.write('No \'networks\' section in config.', debug.levels.Error)
                raise SystemExit(1)

            debug.write('Initialized config.', debug.levels.Info)

        except Exception as e:
            debug.exception('Failed to initialize config.', e)
            raise SystemExit(1)

    else:
        message = '''\
        The config file we've been given does not exist.
        File: "{0}"
        Please use the xbotpp-setup utility to create a configuration,
        or xbotpp-migrate to migrate a pre-v0.3.x config.'''

        debug.write(message.format(options.config), debug.levels.Error)
        raise SystemExit(1)

    # Select network
    global state
    if options.network in config['networks']:
        state['network'] = options.network
        debug.write("Network: %s" % state['network'], debug.levels.Info)
    else:
        debug.write('Unknown network.', debug.levels.Error)
        raise SystemExit(2)

    p = config['networks'][state['network']]['protocol']
    print(dir(protocol))
    if p in dir(protocol):
        state['connection'] = eval('protocol.%s.%s' % (p, p))(config, state)

    print(repr(state))
