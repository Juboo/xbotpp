# vim: noai:ts=4:sw=4:expandtab:syntax=python

import nose
import unittest
import xbotpp.ptr


class test_ptr(unittest.TestCase):
    '''Test that fancy dictionary thing.'''

    def setUp(self):
        self.ptr = xbotpp.ptr()
        self.obj = {'one': 1, 'two': 2, 'three': 3}
        self.ptr.obj_set(self.obj)

    def test_ptr_isinstance(self):
        assert isinstance(self.ptr, xbotpp.ptr)

    def test_ptr_keys_are_equal(self):
        assert self.ptr.keys() == self.obj.keys()

    def test_ptr_get_items(self):
        for key in self.obj.keys():
            assert self.ptr[key] == self.obj[key]

    def test_ptr_del_item(self):
        del self.obj['one']
        with self.assertRaises(KeyError):
            repr(self.obj['one'])

    def test_ptr_len(self):
        assert len(self.ptr) == len(self.obj)

    def test_ptr_repr(self):
        assert repr(self.ptr) == repr(self.obj)

    def test_ptr_internal_object_equals_object(self):
        assert self.ptr.obj_get() == self.obj

    def test_ptr_reassign_object(self):
        tobj = {'hello': 'world'}
        self.ptr.obj_set(tobj)

    def test_ptr_objects_equal_after_reassign(self):
        tobj = {'hello': 'world'}
        self.ptr.obj_set(tobj)
        assert self.ptr.obj_get() == tobj
