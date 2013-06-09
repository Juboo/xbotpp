# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json

class event:
    class generic:
        pass

    class message(generic):
        def __init__(self, source, target, message):
            self.source = source
            self.target = target
            self.message = message

class handlers:
    def __init__(self):
        pass

    def on_message(self, event):
        print(event.text)
