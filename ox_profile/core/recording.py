"""Module for recording and saving measuremnts.
"""

import re


class ProfileRecord(object):
    """Simple record to track how many times a function/path is called.
    """

    def __init__(self, name, hits):
        """Initializer.

        :param name:   String name of function or stack path.

        :param hits:   Number of times it is called.
        """
        self.name = name
        self.hits = hits


class CountingRecorder(object):
    """Recorder which just counts how many times something is called.
    """

    def __init__(self):
        self.my_db = {}

    def record(self, measurement):
        """Record a measurement.

        :param measurement:     An ox_profile.core.metrics.Meaasurement
                                for profiling the program.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  This method is called to record a measurement. Different
                  recorders may track different things about a measurement.

        """
        record = self.my_db.get(measurement.name, 0)
        self.my_db[measurement.name] = record + 1

    def query(self, re_filter='.*', max_records=10):
        """Query the database of measurements.

        :param re_filter='.*':      String regular expression for records
                                    to include in query.

        :param max_records=10:      Maximum number of records to include.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:   The pair (result, count) where count num_records is the
                   total number of records in the database and result is
                   a list of ProfileRecord instances sorted to start from the
                   record with the most hits to the least with at most
                   max_records included.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Query the database.

        """
        regexp = re.compile(re_filter)
        calls = {}
        num_records = len(self.my_db)
        for name, item in self.my_db.items():
            name_list = name.split(';')
            for fname in name_list:
                if regexp.search(fname):
                    calls[fname] = calls.get(fname, 0) + item
        my_hits = list(reversed(sorted(calls.items(),
                                       key=lambda pair: pair[1])))
        result = [ProfileRecord(name, hits) for name, hits in my_hits[
            :max_records]]
        return result, num_records
