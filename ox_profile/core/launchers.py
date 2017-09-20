"""Module containing profiling launchers.
"""

import time
import logging
import threading


from ox_profile.core import sampling, recording


class SamplingTracker:

    def __init__(self):
        self.calls = 0
        self.wait = 0.0
        self.wait_sq = 0.0

    def reset(self):
        self.calls = 0
        self.wait = 0.0
        self.wait_sq = 0.0

    def snap(self, prev):
        my_wait = time.time() - prev
        self.calls += 1
        self.wait += my_wait
        self.wait_sq += my_wait**2

    def stats(self):
        if self.calls == 0:
            return 'No samples taken'

        mean = self.wait/self.calls
        return {'mean': mean,
                'stdev': (self.wait_sq/self.calls - mean**2)**0.5}

class SimpleLauncher(threading.Thread):
    """Simple profiling launcher.
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

    def set_interval(self, new_interval):
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
            time.sleep(self.interval)
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
