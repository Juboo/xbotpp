# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp import debug
from xbotpp.handler import event

dispatch = {
    'message': [],
    'user_join': [],
    'user_part': [],
    'user_change_nick': [],
}

class EventNotFound(BaseException):
    '''\
    Thrown by :func:`bind_event` when an event that is being bound to
    does not exist.
    '''

    pass

def bind_event(event, handler):
    '''\
    Adds the function `handler` to the :data:`event dispatch list <dispatch>` for `event`.
    '''

    global dispatch
    if event in dispatch:
        dispatch[event].append(handler)
    else:
        raise EventNotFound()

def on_message(revent):
    '''\
    Dispatches :class:`message events <xbotpp.handler.event.message>`.
    '''

    for function in dispatch['message']:
        function(revent)

def on_user_join(revent):
    '''\
    Dispatches :class:`user join events <xbotpp.handler.event.user_join>`.
    '''

    for function in dispatch['user_join']:
        function(revent)

def on_user_part(revent):
    '''\
    Dispatches :class:`user part events <xbotpp.handler.event.user_part>`.
    '''

    for function in dispatch['user_part']:
        function(revent)

def on_user_change_nick(revent):
    '''\
    Dispatches :class:`user nick change events <xbotpp.handler.event.user_change_nick>`.
    '''

    for function in dispatch['user_change_nick']:
        function(revent)
