# vim: noai:ts=4:sw=4:expandtab:syntax=python

import xbotpp.modules
import re


__xbotpp_module__ = "newtest"

@xbotpp.modules.on_event('message')
def message_handler(event):
    print("(type %s) %s -> %s: %s" % (event.type, event.source, event.target, event.message))
    if re.match('reload', event.message):
        xbotpp.state['modules_monitor'].unload('newtest')
