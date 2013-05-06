# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import nose
import inspect
import unittest
from mock_classes import *


class test_botio(unittest.TestCase):

    @classmethod
    def setup_class(self):
        self.bot = Bot()

    def test_issue_command(self):
        client = IrcClient()
        event = IrcEvent()

        event.arguments = ["!test_bind"]
        event.target = "TEST_TARGET"

        self.bot.botio.read(client, event)
        assert ("TEST_TARGET", "Test Module") in client.messagebuffer, "Command failed to return expected value"

    def test_issue_command_with_args(self):
        client = IrcClient()
        event = IrcEvent()

        event.arguments = ["!test_args one two"]
        event.target = "TEST_TARGET"

        self.bot.botio.read(client, event)
        assert ("TEST_TARGET", "Arguments: one two") in client.messagebuffer, "Command failed to return expected value"

    def test_issue_command_chain(self):
        client = IrcClient()
        event = IrcEvent()

        event.arguments = ["!test_bind | test_buffer"]
        event.target = "TEST_TARGET"

        self.bot.botio.read(client, event)
        assert ("TEST_TARGET", "Buffer: Test Module") in client.messagebuffer, "Command failed to return expected value"

