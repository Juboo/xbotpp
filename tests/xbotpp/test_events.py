# vim: noai:ts=4:sw=4:expandtab:syntax=python

import nose
import unittest
import xbotpp
import xbotpp.util
import xbotpp.handler
import xbotpp.modules


__xbotpp_module__ = "test_events"

class Namespace: 
    pass

class test_events(unittest.TestCase):
    '''Test the event handling functions of xbot++.'''

    def setUp(self):
        xbotpp.state = xbotpp.ptr()
        xbotpp.state['modules_monitor'] = xbotpp.modules.monitor()

    def test_add_invalid_event_raises_exception(self):
        with self.assertRaises(xbotpp.handler.handlers.EventNotFound):
            xbotpp.handler.handlers.bind_event('this_will_not_exist_ever', lambda x: x)

    def test_add_valid_event(self):
        xbotpp.handler.handlers.bind_event('message', lambda x: x)

    def test_send_event(self):
        a = Namespace()

        a.b = False
        def handler(revent):
            a.b = revent

        event = xbotpp.handler.event.message('source', 'target', 'message', 'type')
        xbotpp.handler.handlers.bind_event('message', handler)
        xbotpp.handler.handlers.on_message(event)

        assert a.b != False, 'Event not raised'

        for t in ['source', 'target', 'message', 'type']:
            one = getattr(a.b, t, None)
            two = getattr(event, t, None)
            assert one == two, 'Event %s was not what was sent (got \'%s\', expected \'%s\')' % (t, one, two)

    def test_bind_event_with_decorator(self):
        a = Namespace()
        a.b = False

        @xbotpp.modules.on_event('message')
        def handler(revent):
            a.b = revent

        event = xbotpp.handler.event.message('source', 'target', 'message', 'type')
        xbotpp.handler.handlers.on_message(event)

        assert a.b != False, 'Event not raised'

        for t in ['source', 'target', 'message', 'type']:
            one = getattr(a.b, t, None)
            two = getattr(event, t, None)
            assert one == two, 'Event %s was not what was sent (got \'%s\', expected \'%s\')' % (t, one, two)

    def test_multiple_fired_events(self):
        a = Namespace()
        a.b = []

        for i in range(0, 10):
            @xbotpp.modules.on_event('message')
            @xbotpp.util.change_name("handler_{}".format(i))
            def handler(revent):
                a.b.append(revent)

        event = xbotpp.handler.event.message('source', 'target', 'message', 'type')
        xbotpp.handler.handlers.on_message(event)

        assert a.b != [], 'Event not raised'
        assert len(a.b) is 10, 'Wrong number of events in namespace: should be 10, got %d' % len(a.b)

        for i in a.b:
            for t in ['source', 'target', 'message', 'type']:
                one = getattr(i, t, None)
                two = getattr(event, t, None)
                assert one == two, 'Event %s was not what was sent (got \'%s\', expected \'%s\')' % (t, one, two)
