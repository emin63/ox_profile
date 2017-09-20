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
        frames_dict = sys._current_frames()  # pylint: disable=protected-access
        measure_tool = self.get_measure_tool()
        for frame_id, frame in frames_dict.items():
            logging.debug('Recording frame with id %s', str(frame_id))
            measure = measure_tool(frame)
            self.my_db.record(measure)

    def __call__(self, *args, **kwargs):
        "Syntactic sugar to call `self.run(*args, **kwargs)`."

        return self.run(*args, **kwargs)
