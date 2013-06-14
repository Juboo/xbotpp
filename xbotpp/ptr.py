# vim: noai:ts=4:sw=4:expandtab:syntax=python


class ptr:
    '''Kind of like a pointer to a dictionary.'''

    def __init__(self):
        self.obj = {}

    def __setitem__(self, index, value):
        self.obj[index] = value

    def __getitem__(self, index):
        if index not in self.obj:
            raise KeyError(index)
        return self.obj[index]

    def __delitem__(self, index):
        if index not in self.obj:
            raise KeyError(index)
        del self.obj[index]

    def __len__(self):
        return len(self.obj)

    def __iter__(self):
        for obj in self.obj:
            yield obj

    def __repr__(self):
        return repr(self.obj)

    def keys(self):
        return self.obj.keys()

    def obj_get(self):
        return self.obj

    def obj_set(self, obj):
        self.obj = obj
