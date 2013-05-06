# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import nose
import inspect
import unittest
from mock_classes import *


class test_modules(unittest.TestCase):

    @classmethod
    def setup_class(self):
        self.bot = Bot()
        self.bot.debug = True

    def test_modules_loaded_modules(self):
        loaded = []
        for module in enumerate(self.bot.modules.modules['command']):
            loaded.append(module[1])

        assert 'test_no_bind' in loaded, "test_no_bind module not loaded"
        assert 'test_bind' in loaded, "test_bind module not loaded"

        assert self.bot.modules.modules['command']['test_no_bind'].func(self.bot, "", [""], "") == "Test Module", "Test module test_no_bind produced unknown return value"
        assert self.bot.modules.modules['command']['test_bind'].func(self.bot, "", [""], "") == "Test Module", "Test module test_bind produced unknown return value"

    def test_modules_unload_returns_false_for_nonexistant_module(self):
        assert self.bot.modules.unload("module_that_does_not_exist") == False, "Unload returned not False for non-existant module"

    def test_modules_unload_module(self):
        assert self.bot.modules.unload("test_bind") == True, "Unload did not return True for module that exists"

    def test_modules_load_module(self):
        assert self.bot.modules.load("test_bind") == True, "Load did not return True for module that exists"

    def test_modules_reload_module(self):
        assert self.bot.modules.load("test_no_bind") == True, "Load did not return True for module that exists and is already loaded"

