"""Module for handling measurement and sampling of data.
"""


class Measurement(object):
    """Measurement of profiling information.

    The idea is that you initialize an instance of a Measurement when
    you want to get some profiling information about a program.
    """

    def __init__(self, frame):
        """Initializer.

        :param frame:    Stack frame to measure.

        """
        self.name = self.snap(frame)

    def get_path(self):
        """Return backtrace path for snapped measurement.
        """
        return self.name.split(';')

    def snap(self, frame):
        """Snap a measurement for the given stack frame (called by __init__).

        :param frame:     Stack frame to take a measurement about.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:   String representing nicely formatted backtrace of functions
                   for given stack frame.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Meant to be called internally by __init__ to snap a
                   measurement.

        """
        stack = []
        self.name = '{}({})'.format(frame.f_code.co_name,
                                    frame.f_globals.get('__name__'))
        while frame is not None:
            formatted_frame = '{}({})'.format(frame.f_code.co_name,
                                              frame.f_globals.get('__name__'))
            stack.append(formatted_frame)
            frame = frame.f_back

        formatted_stack = ';'.join(reversed(stack))
        return formatted_stack
