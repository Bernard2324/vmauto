from threading import Thread


class Asynchronous(object):

    def __init__(self, *args, **kwargs):
        self.thread = None

    def __call__(self, function):
        def inner_wrapper(*args, **kwargs):
            self.thread = Thread(target=function, args=args, kwargs=kwargs)
            self.thread.start()
            return self.thread
        return inner_wrapper


class AsynchronousRoutine(Thread):

    def _init__(self, FrozenSet, callback):
        self.data_set = FrozenSet
        self.callback = callback
        Thread.__init__(self)

    def grab(self):
        if len(self.data_set) > 0:
            return self.data_set.pop()
        else:
            raise IndexError('No More Instances to Grab')

    def run(self):
        while True:
            try:
                current_task = self.grab()
            except IndexError:
                break

            self.callback(current_task)