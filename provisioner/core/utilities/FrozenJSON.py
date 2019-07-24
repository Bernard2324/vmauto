import collections
import keyword

__author__ = {'FluentPython': 'Luciano Ramalho',
              'Modification': 'Maurice Green'}


class FrozenJSON(object):
    '''

    This is a FrozenJSON class that uses __getattr__ to locate nested values in a dictionary/json mapping
    This means rather than typing venue['events']['dates'] you can type venue.events.dates[0].

    This concept was pulled from FluentPython book, and slightly modified for Apex use
    '''
    def __init__(self, mapping):

        # verify that the passed mapping is a valid mapping
        self.__data = {}

        for key,value in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = value

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return FrozenJSON.build(self.__data[name])

    def __iter__(self):
        return iter(self.__data)

    @classmethod
    def build(cls, obj):
        if isinstance(obj, collections.Mapping):
            return cls(obj)
        elif isinstance(obj, collections.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj
