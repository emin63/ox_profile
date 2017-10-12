"""Flask Blueprint for ox_Profile.

This module provides the OX_PROF_BP variable representing the main
ox_profile blueprint. If you are incorporating ox_profile into your own
flask application, you should call register_blueprint(OX_PROF_BP)
appropriately.
"""

import collections
import threading
import logging
import copy


from flask import Blueprint

from ox_profile.core import launchers


ReqRecord = collections.namedtuple('ReqRecord', ['start_time', 'end_time'])

class OxProfBlueprint(Blueprint):
    """Subclass flask Blueprint to provide custom blueprint for ox_profile.

    """

    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)
        self.req_db = {}
        self.db_lock = threading.Lock()
        self.launcher = launchers.SimpleLauncher()

    def record_req(self, username, endpoint, stime, etime):
        """Record request information.

        :param username:        String username initiating request.

        :param endpoint:        String name of endpoint.

        :param stime:    A datetime.datetime in UTC for start time.

        :param etime:    A datetime.datetime in UTC for end time.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Record data about a completed request. Expected to
                  be called by something in teardown_app_request.

        """
        with self.db_lock:
            key = (username, endpoint)
            record = self.req_db.get(key, [])
            if not record:
                self.req_db[key] = record
            record.append(ReqRecord(stime, etime))

    def get_reqs(self):
        """Return a copy of self.req_db.
        """
        with self.db_lock:
            return copy.deepcopy(self.req_db)

    def register(self, app, *args, **kwargs):
        """Override default register method to also activate plugins.

        :arg app, *args, **kwargs:  As for usual Blueprint.register method.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  As usual for Blueprint.register.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Override registration so we can start plugins.

        """
        result = Blueprint.register(self, app, *args, **kwargs)
        logging.debug('Registered ox_profile blueprint')
        return result

    @staticmethod
    def get_help():
        "Get some help (point user to github repo)."
        print('Please see github repo for ox_profile more information.')


OX_PROF_BP = OxProfBlueprint(
    'ox_profile', __name__, template_folder='templates',
    static_folder='static', url_prefix='/ox_profile')
