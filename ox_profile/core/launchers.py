"""Module containing profiling launchers.
"""

import doctest
import time
import logging
import threading


from ox_profile.core import sampling, recording


class SamplingTracker:
    """Simple class to track how often we sample things.

    This class is meant to track how often we take samples. Since we are
    doing stastitical profiling, the interval between samples is random
    and can be affected by many things. The SamplingTracker is used
    to follow that.

    Usually you do not need to worry much about this and can just use
    the SimpleLauncher which has an instance of a SamplingTracker.
    """

    def __init__(self):
        self.calls = 0
        self.wait = 0.0
        self.wait_sq = 0.0

    def reset(self):
        "Reset everything in the tracker."
        self.calls = 0
        self.wait = 0.0
        self.wait_sq = 0.0

    def snap(self, prev):
        """Snap a sample remember how far it was since the previous snap.

        The `prev` argument represents the `time.time()` of the previous
        snap. We then save the `time.time()` from now to prev.
        """
        my_wait = time.time() - prev
        self.calls += 1
        self.wait += my_wait
        self.wait_sq += my_wait**2

    def stats(self):
        "Return dictionary of stats related to snap interval."
        if self.calls == 0:
            return 'No samples taken'

        mean = self.wait/self.calls
        return {'mean': mean,
                'stdev': (self.wait_sq/self.calls - mean**2)**0.5}


class SimpleLauncher(threading.Thread):
    """Simple profiling launcher.

The `SimpleLauncher` is top-level class to do statistical
profiling. While some features are configurable, the simplest thing to
do is just instantiate an instance of this class and call its
`unpause` method to start profiling.

Basically, what this class does is:

  1. Creates an instance of the `Sampler` class with reasonable defaults.
  2. Initializes itself as a daemon thread and starts.
  3. Pauses itself so the thread does nothing so as to not load the system.
  4. Provides an `unpause` method you can use when you want to turn on
     profiling.
  5. Provides a `pause` method if you want to turn off profiling.


Example usage is shown below:

>>> import random, math, time
>>> from ox_profile.core import launchers
>>> launcher = launchers.SimpleLauncher()
>>> def example_func(x):
...     return [math.atanh(random.uniform(0,1)) for i in range(x)]
...
>>> launcher.start()
>>> launcher.unpause()
>>> dummy = [example_func(i) for i in range(2000)]
>>> query, total_records = launcher.sampler.my_db.query()
>>> info = ['%s: %s' % (i.name, i.hits) for i in query]
>>> print('Items:%s' % (('%c - ' % 10).join([''] + info)))# doctest: +ELLIPSIS
Items:
 - ...
 - ...
>>> launcher.cancel()  # This turns off the profiler for good

    """

    def __init__(self, sampler=None, stop_flag=None, interval=.001,
                 *args, **kwargs):
        """Initializer.

        :param sampler=None:   Instance of a profiling sampler such as
                               `ox_profile.core.sampling.Sampler` (which is
                               used as default if sampler is None).

        :param stop_flag=None: Optional threading.Event to use in forcing the
                               thread to stop. If None, then one will be
                               created so you can stop via `self.cancel()`.

        :param interval=.001:  How often (in seconds) to sample the program.

        :param *args, **kwargs:  Passed to threading.Thread.__init__.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:      The profiler is basically running as a daemon thread
                      and continusly

        """
        self.tracker = SamplingTracker()
        self.sampler = sampler if sampler else sampling.Sampler(
            recording.CountingRecorder())
        self.interval = interval
        self.stop_flag = stop_flag if stop_flag else threading.Event()
        self.stop_flag.clear()
        self.unpaused = threading.Event()
        self.pause()
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        assert self.isDaemon()

    @classmethod
    def launch(cls):
        """Syntatic sugar for calling s=cls(), s.start() then s.unpause().
        """
        result = cls()
        result.start()
        result.unpause()
        return result

    def show(self, *args, **kwargs):
        """Syntatic sugar for calling self.sampler.show(*args, **kwargs).

        Returns string describing results.
        """
        return self.sampler.show(*args, **kwargs)

    def query(self, *args, **kwargs):
        """Syntatic sugar for calling self.sampler.query(*args, **kwargs).

        Returns string describing results.
        """
        return self.sampler.query(*args, **kwargs)

    def set_interval(self, new_interval):
        """Set the interval for how often we take a sample.

        :arg new_interval:  Float between 0 and 10 for how long to
                            wait beteeen samples.
        """
        assert new_interval > 0 and new_interval < 10
        self.interval = new_interval
        self.tracker.reset()

    def pause(self):
        """Pause profiling until self.unpause() is called.
        """
        self.unpaused.clear()

    def unpause(self):
        """Un-pause profiling if paused.

        Note that you must call `self.start()` to initially start and trying
        to unpause before calling `self.start()` will not doo much.  Note this
        is a *thread* so you should call `self.start()` *NOT* `self.run()`.
        """
        self.unpaused.set()

    def is_paused(self):
        """Return whether we are paused or not (see pause/unpause methods).
        """
        return not self.unpaused.is_set()

    def run(self):
        """Start running the profiler.

        *IMPORTANT*:  This is a *thread* so you should call `self.start()`
                      *NOT* `self.run()`. Do *NOT* call self.run directly.
        """
        logging.info('Starting Launcher')
        prev = time.time()
        while not self.stop_flag.is_set():
            interval = self.interval
            time.sleep(interval)
            self.tracker.snap(prev)
            self.unpaused.wait()
            prev = time.time()
            self.sampler()

        logging.info('Stopping Launcher')

    def cancel(self):
        """Cancel the running profiler.

        This is useful since the profiler is a thread. Although pause will
        pause the thread, you need to call cancel (and make sure it is
        unpaused) for the thread to actually exit.
        """
        self.stop_flag.set()


if __name__ == '__main__':
    # Run doctest if file executed as a script
    doctest.testmod()
    print('Finished Tests')
