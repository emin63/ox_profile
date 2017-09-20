"""Flask Blueprint for ox_Profile.

This module provides the OX_PROF_BP variable representing the main
ox_profile blueprint. If you are incorporating ox_profile into your own
flask application, you should call register_blueprint(OX_PROF_BP)
appropriately.
"""

import logging

from flask import Blueprint

from ox_profile.core import launchers


class OxProfBlueprint(Blueprint):
    """Subclass flask Blueprint to provide custom blueprint for ox_profile.

    """

    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)
        self.launcher = launchers.SimpleLauncher()

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
