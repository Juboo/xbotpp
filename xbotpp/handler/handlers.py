# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp import debug
from xbotpp.handler import event

dispatch = {
    'message': [],
    'user_join': [],
    'user_part': [],
    'user_change_nick': [],
}

def on_message(revent):
    for function in dispatch['message']:
        function(revent)

def on_user_join(revent):
    for function in dispatch['user_join']:
        function(revent)

def on_user_part(revent):
    for function in dispatch['user_part']:
        function(revent)

def on_user_change_nick(revent):
    for function in dispatch['user_change_nick']:
        function(revent)
