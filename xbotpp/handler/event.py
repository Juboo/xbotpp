# vim: noai:ts=4:sw=4:expandtab:syntax=python

class generic:
    pass

class message(generic):
    def __init__(self, source, target, message):
        self.source = source
        self.target = target
        self.message = message

class user_join(generic):
    def __init__(self, user):
        self.user = user

class user_part(generic):
    def __init__(self, user):
        self.user = user

class user_change_nick(generic):
    def __init__(self, before, after):
        self.before = before
        self.after = after
