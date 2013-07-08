# vim: noai:ts=4:sw=4:expandtab:syntax=python

import nose
import unittest
import xbotpp
import xbotpp.protocol.irc
import xbotpp.debug
import xbotpp.util.classes


class test_irc_serverspec(unittest.TestCase):
    '''Test the IRC protocol server specification class.'''

    def test_serverspec_stringify_default_port(self):
        spec = xbotpp.protocol.irc.ServerSpec('host')
        assert str(spec) == 'host:6667'

    def test_serverspec_stringify_custom_port(self):
        spec = xbotpp.protocol.irc.ServerSpec('host', 6697)
        assert str(spec) == 'host:6697'

    def test_serverspec_stringify_with_password(self):
        spec = xbotpp.protocol.irc.ServerSpec('host', 6697, 'password')
        assert str(spec) == 'host:6697'

class test_irc(unittest.TestCase):
    '''Test the IRC protocol class.'''

    def setUp(self):
        xbotpp.debug.permanent_silence()

        xbotpp.config = xbotpp.util.classes.ptr()
        xbotpp.config.obj_set({
            'bot': {
                'prefix': '!',
                'owner': 'akiaki',
            },
            'networks': {
                'localhost': {
                    'protocol': 'irc',
                    'servers': ['localhost:6667'],
                    'nick': 'xbotpp',
                    'channels': ['#xbotpp'],
                    'server_password': 'test_password',
                },
            },
            'modules': {
                'load': ['newtest'],
                'paths': ['./modules'],
            },
        })

        xbotpp.state = xbotpp.ptr()
        xbotpp.state.obj_set({
            'network': 'localhost',
        })

        self.irc = xbotpp.protocol.irc.irc()

    def test_irc_network_is_correct(self):
        assert self.irc.network == xbotpp.config['networks']['localhost']

    def test_irc_nickname_is_correct(self):
        assert self.irc._nickname == xbotpp.config['networks']['localhost']['nick']

    def test_irc_realname_is_bot_owner(self):
        assert self.irc._realname == xbotpp.config['bot']['owner']
        
    def test_irc_hosts_are_serverspec_objects(self):
        for host in self.irc.hosts:
            assert isinstance(host, xbotpp.protocol.irc.ServerSpec)

    def test_irc_host_is_correct(self):
        spec = xbotpp.protocol.irc.ServerSpec('localhost', 6667)
        assert str(self.irc.hosts[0]) == str(spec)

    def test_irc_server_password_is_not_none(self):
        assert self.irc.hosts[0].password != None

    def test_irc_server_password_is_correct(self):
        assert self.irc.hosts[0].password == xbotpp.config['networks']['localhost']['server_password']
