"""Tools to sample running programs.
"""

import logging
import sys

from ox_profile.core import metrics


class Sampler(object):
    """Basic class to sample program for statistical profiling.
    """

    def __init__(self, my_db):
        self.my_db = my_db

    def get_measure_tool(self):
        """Get a class or function to call to take a measurement.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:  class or function to call to take a measurement.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  This method provides the "measurement tool" we are going
                  to use in profiling. Sub-classes could override this to
                  take different kinds of measurements.

        """
        dummy = self
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
        "Syntactic sugar to call `self.run(*args, **kwargs)`."

        return self.run(*args, **kwargs)
