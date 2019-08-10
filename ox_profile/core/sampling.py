"""Tools to sample running programs.
"""

import doctest
import logging
import sys

from ox_profile.core import metrics


class Sampler(object):
    """Basic class to sample program for statistical profiling.

This is the workhorse for ox_profile to do statistical sampling.
At a low level, we do this sampling using `sys._current_frames`. As
suggested by the leading underscore, this system function may be a bit
less robust. Indeed, the documentation says "This function should be
used for specialized purposes only." Hopefully the core python
developers will not make major changes to such a useful function.

The most interesting method is `run` which:

  1. Uses `sys.setswitchinterval` to try and prevent a thread context switch.
  2. Calls `sys._current_frames` to sample what the python interpreter is
     doing.
  3. Updates a simple in-memory database of what functions are running.

In principle, you could just use the Sampler via something like

>>> from ox_profile.core import sampling, recording
>>> sampler = sampling.Sampler(recording.CountingRecorder())
>>> def foo():
...     sampler.run()
...     return 'done'
...
>>> dummy = foo()
>>> info, calls = sampler.my_db.query()
>>> pretty = ('%c'%10).join(map(str, info))
>>> print('%i calls:%c%s' % (calls, 10, pretty)) # doctest: +ELLIPSIS
1 calls:
ProfileRecord(...)

The above would have the sampler take a snapshot of the stack frames
when the `foo` function is run. Of course, this isn't very useful by
itself because it just tells you that `foo` is being run. It could be
useful if there were other threads which were running because the
sampler would tell you what stack frame those threads were in. For
this reason you should use the SimpleLauncher class in
the `ox_profile/core/launchers` module which creates an instance
of this class.

    """

    def __init__(self, my_db):
        self.my_db = my_db

    def show(self, *args, **kwargs):
        """Syntactic sugar self.my_db.show(*args, **kwargs) to show results.

        Returns a string describing collected data.
        """
        return self.my_db.show(*args, **kwargs)

    def query(self, *args, **kwargs):
        """Syntactic sugar self.my_db.query(*args, **kwargs) to query results.

        Returns a string describing collected data.
        """
        return self.my_db.query(*args, **kwargs)

    def get_measure_tool(self):
        """Get a class or function to call to take a measurement.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:  class or function to call to take a measurement.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  This method provides the "measurement tool" we are going
                  to use in profiling. Sub-classes could override this to
                  take different kinds of measurements.

        """
        return metrics.Measurement

    def run(self):
        """Run the sampler to make a measurement of the current stack frames.
        """
        measure_tool = self.get_measure_tool()

        # Muck with switch interval to prevent thread context switching while
        # trying to capture profiling information for safety

        switch_interval = sys.getswitchinterval()
        try:
            logging.debug('Process sampling')
            sys.setswitchinterval(10000)
            for dummy_frame_id, frame in (
                    sys._current_frames(  # pylint: disable=protected-access
                        ).items()):
                self.my_db.record(measure_tool(frame))
        finally:
            sys.setswitchinterval(switch_interval)
        logging.debug('Switch interval now %.2f', sys.getswitchinterval())

    def __call__(self, *args, **kwargs):
        """Syntactic sugar to call `self.run(*args, **kwargs)`."""

        return self.run(*args, **kwargs)


if __name__ == '__main__':
    # Run doctest if file executed as a script
    doctest.testmod()
    print('Finished Tests')
