# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json
import inspect
import importlib
import argparse
import xbotpp.debug
import xbotpp.util
import xbotpp.util.classes


__version__ = 'v0.3.2'
config = xbotpp.util.classes.ptr()
state = xbotpp.util.classes.EmptyClass()
vendor = xbotpp.util.classes.EmptyClass()
vendor_modules = ['sqliteshelf']


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

    xbotpp.debug.print_flagged = e
    xbotpp.debug.write('Debugging information has been %s.' % 'enabled' if e else 'disabled', xbotpp.debug.levels.Info)

def save_config():
    fh = open(state.configfile, 'w+')
    json.dump(config.obj_get(), fh, indent=4, separators=(',', ': '), sort_keys=True)
    fh.close()

def load_config():
    config.obj_set(json.load(open(state.configfile, 'r')))

def init(options):
    '''Initialize the bot and load our configuration.'''

    import xbotpp.handler
    import xbotpp.modules
    import xbotpp.protocol

    xbotpp.debug.write('Entered init().')

    state.path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    xbotpp.debug.write('Script directory: {}'.format(repr(state.path).replace('\\\\', '\\')))

    xbotpp.debug.write('Importing vendor modules...')
    for mod in vendor_modules:
        path = os.path.join(state.path, 'vendor', mod)
        sys.path.insert(0, path)
        setattr(xbotpp.vendor, mod, importlib.import_module(mod))
        xbotpp.debug.write('{}: okay'.format(mod))

    xbotpp.debug.write('Loading config...')
    if os.path.exists(options.config):
        try:
            state.configfile = options.config
            load_config()

            if not 'networks' in config:
                xbotpp.debug.write('No \'networks\' section in config.', xbotpp.debug.levels.Error)
                raise SystemExit(1)

            xbotpp.debug.write('Initialized config.', xbotpp.debug.levels.Info)

        except Exception as e:
            xbotpp.debug.exception('Failed to initialize config.', e)
            raise SystemExit(1)

    else:
        message = '''\
        The config file we've been given does not exist.
        File: "{0}"
        Please use the xbotpp-setup utility to create a configuration,
        or xbotpp-migrate to migrate a pre-v0.3.x config.'''

        xbotpp.debug.write(message.format(options.config), xbotpp.debug.levels.Error)
        raise SystemExit(1)

    # Select network
    if options.network in config['networks']:
        state.network = options.network
        xbotpp.debug.write("Network: %s" % state.network, xbotpp.debug.levels.Info)
    else:
        xbotpp.debug.write('Unknown network.', xbotpp.debug.levels.Error)
        raise SystemExit(2)

    # Set up module monitor
    state.modules = modules.monitor()
    state.modules.load_init()

    # Set up our protocol library
    p = config['networks'][state.network]['protocol']
    if p in dir(protocol):
        state.connection = eval('protocol.%s.%s' % (p, p))()
    else:
        xbotpp.debug.write('''Protocol handler for network not found (network protocol: '%s')''' % p, xbotpp.debug.levels.Error)
        raise SystemExit(2)

    # and start
    state.connection.start()

    # when we escape from that, save our config
    save_config()    
