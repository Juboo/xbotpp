# vim: noai:ts=4:sw=4:expandtab:syntax=python

class generic:
    '''\
    A generic event.
    '''

    pass

class message(generic):
    '''\
    Fired when a message is recieved by the bot.

    `etype` should be one of `privmsg` (private message to the bot),
    `pubmsg` (a public message), or `notice`.
    '''

    def __init__(self, source, target, message, etype):
        self.source = source
        self.target = target
        self.message = message
        self.type = etype

class user_join(generic):
    '''\
    Fired when a user joins a channel the bot is in.
    '''

    def __init__(self, user):
        self.user = user

class user_part(generic):
    '''\
    Fired when a user leaves a channel the bot is in.
    '''

    def __init__(self, user):
        self.user = user

class user_change_nick(generic):
    '''\
    Fired when either:

    (1) The bot changes it's nick
    (2) A user in a channel the bot is in has changed their nick
    '''

    def __init__(self, before, after):
        self.before = before
        self.after = after
