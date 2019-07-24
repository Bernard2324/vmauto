from __future__ import print_function
import pickle
import os
import time
import hashlib

__author__ = 'Maurice Green'


class CheckCache(object):
    '''
    This is a decorator for caching objects with Pickle, in self.cache_dir.
    The main benefit of this, is to dramatically cutdown on the number of API
    calls being made, and thus save overhead.  Certain calls, like salt/modules/checkmk::_get_all_hosts(),
    would benefit from having the returned list of hostnames stored by pickle, and then retrieved upon request,
    rather than making unnecessary api calls every time.

    secondary functions can then use this stored data, which chaining multiple calls to satisfy a request for
    one set of data.

    The pickle object is stored in self.cache_dir, and the value 'seconds' determines how long the cached object
    should be considered valid.

    os.path.getatime() [get last access time] will be subtracted from current time, to determine if the 'elapsed_time'
    is less than 'seconds'.  If it is, the cached pickle object will be returned, and the functions api call, will be skipped.
    The function will actually be skipped altogether.  If the cached pickle object is too old, the function will be executed,
    and the api called.  The data will be handled accordingly, stored as a pickle object for utilization next time, and
    returned.
    '''
    def __init__(self, *args, **kwargs):
        if not kwargs.get('seconds') or \
                not kwargs.get('cache_dir', False):
            raise ValueError('Must Supply valid **kwargs, \'seconds\' and \'cache_dir\'')

        self.seconds = kwargs['seconds']
        self.cache_dir = kwargs['cache_dir']

    def __call__(self, function):
        def inner_wrapper(*args, **kwargs):
            if not os.path.exists(self.cache_dir):
                os.mkdir(self.cache_dir)

            stashkey = hashlib.sha1(str(function.__name__)).hexdigest()
            file_path = os.path.join(self.cache_dir, stashkey)

            if os.path.exists(file_path):
                file_creation_time = os.path.getctime(file_path)
                time_elapsed = time.time() - file_creation_time
                if time_elapsed < self.seconds:
                    return pickle.load(open(file_path, 'r'))

            data = function(*args, **kwargs)
            pickle.dump(data, open(file_path, 'wb'))
            return data
        return inner_wrapper