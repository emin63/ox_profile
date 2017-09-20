"""Basic views for ox_profile flask UI.
"""

import logging
from functools import wraps

from flask import request, Markup, current_app, render_template, url_for
from flask.ext.login import login_required
from flask.ext.login import current_user

from ox_profile.ui.flask import OX_PROF_BP


def access_problem_p():
    """If user is allowed access to ox_profile, return None else return error.

    This is meant to be called when a user tries to access ox_profile routes
    so that non-privledged users cannot cause trouble. It looks in
    current_app.config['OX_PROF_USERS'] for a dictionary or set of allowed
    users.
    """
    allowed = current_app.config.get('OX_PROF_USERS', {})
    user = current_user.name
    if user in allowed:
        return None

    msg = 'Current user %s not in the %i allowed ox profile users.%s' % (
        user, len(allowed),
        '\nConfigure app.config["OX_PROF_USERS"] if necessary.')
    return render_template('ox_prof_err.html', error_msg=msg)


def restrict_access(my_func):
    """Simple decorator to call access_problem_p before execution.
    """
    @wraps(my_func)
    def wrapper(*args, **kwds):
        """Check access_problem_p and then execute wrapped function.
        """

        problem = access_problem_p()
        if problem is None:
            return my_func(*args, **kwds)
        return problem

    return wrapper


@OX_PROF_BP.route('/')
@OX_PROF_BP.route('/index')
@login_required
@restrict_access
def index():
    """Top-level index for ox profile.
    """
    commands = [(n, url_for('%s.%s' % ('ox_profile', n))) for n in [
        'status', 'pause', 'unpause']]

    return render_template('ox_prof_intro.html', commands=commands)


@OX_PROF_BP.route('/status')
@login_required
@restrict_access
def status():
    """Show status of current profiling.
    """
    re_filter = request.args.get('re_filter', '.*')
    max_records = int(request.args.get('max_records', 50))

    query, total_records = OX_PROF_BP.launcher.sampler.my_db.query(
        re_filter=re_filter, max_records=max_records)

    return render_template(
        'ox_prof_status.html', launcher=OX_PROF_BP.launcher,
        max_records=max_records, total_records=total_records, query=query)


@OX_PROF_BP.route('/pause')
@login_required
@restrict_access
def pause():
    """Pause the profiler.
    """
    OX_PROF_BP.launcher.pause()
    return render_template('ox_prof_msg.html', message='paused')


@OX_PROF_BP.route('/unpause')
@login_required
@restrict_access
def unpause():
    """Unpause profiler or start it for the first time.
    """
    launcher = OX_PROF_BP.launcher
    msgs = []
    if not launcher.is_alive():
        msgs.append('Started thread for first time')
        launcher.start()
    launcher.unpause()
    msgs.append('unpaused')
    return render_template('ox_prof_msg.html', message=Markup(
        '\n<BR>\n'.join(msgs)))


@OX_PROF_BP.route('/set_interval')
@login_required
@restrict_access
def set_interval():
    "Set the sampling interval"
    interval = request.args.get('interval', None)
    problem = None
    try:
        fint = float(interval)
        if fint < 0:
            raise ValueError('Negative interval of %s illogical.')
        if fint > 10:
            raise ValueError('Interval > 10 is useless.')
    except ValueError as problem:
        logging.debug('Could not convert interval %s to float because %s',
                      interval, problem)
    if problem:
        return render_template('ox_prof_err.html', error_msg=problem)
    OX_PROF_BP.launcher.set_interval(fint)

    return render_template('ox_prof_msg.html', message=(
        'Changed sampling interval to %f' % fint))
