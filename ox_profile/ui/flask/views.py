"""Basic views for ox_profile flask UI.
"""

import urllib.parse
import io
import csv
import collections
import datetime
import logging
from functools import wraps

from flask import (
    request, Markup, current_app, render_template, url_for, g, make_response)
from flask_login import login_required
from flask_login import current_user

from ox_profile.ui.flask import OX_PROF_BP, ReqRecord

RouteInfo = collections.namedtuple('RouteInfo', [
    'name', 'hits', 'avg_time'])

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
        'status', 'pause', 'unpause', 'show_req_times']]

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


@OX_PROF_BP.before_app_request
def monitor_routes():
    """Simple function to record start time of request.

    See monitor_route_completion for more info.
    """
    g.ox_prof_ts = datetime.datetime.utcnow()


@OX_PROF_BP.teardown_app_request
def monitor_route_completion(exception=None):
    """Monitor and record route completion.

    :param exception=None:    Provided by flask if exception happened.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:   Record a few things in OX_PROF_BP about the route that
               just completed for profiling information.

    """
    try:
        user = getattr(current_user, 'name', None)
        if user is None:
            user = getattr(current_user, 'username', 'unknown')
        OX_PROF_BP.record_req(user, request.endpoint, g.ox_prof_ts,
                              datetime.datetime.utcnow())
    except Exception as problem:  # pylint:disable=broad-except
        logging.error('Got problem %s in monitor_route_completion', str(
            problem))


@OX_PROF_BP.route('/show_req_times')
@login_required
@restrict_access
def show_req_times():
    reqs = OX_PROF_BP.get_reqs()
    if int(request.args.get('as_csv', 0)):
        return _make_csv_response('reqs.csv', reqs)

    user_times = {}
    func_times = {}
    for (user, endpoint), time_list in reqs.items():
        runtimes = [(e - s).total_seconds() for s, e in time_list]
        fdata = func_times.get(endpoint, [])
        if not fdata:
            func_times[endpoint] = fdata
        fdata.extend(runtimes)
        udata = user_times.get(user, [])
        if not udata:
            user_times[endpoint] = udata
        udata.extend(runtimes)
    rinfo = [RouteInfo(name, len(data), sum(data)/float(len(data))) for (
        name, data) in func_times.items()]

    result = render_template('ox_prof_rinfo.html', rinfo=reversed(sorted(
        rinfo, key=lambda r: r.avg_time)), csv_link=Markup(make_download_link(
            request, {'as_csv': 1})))

    return result


def _make_csv_response(name, data):
    if isinstance(data, str):
        text = data
    elif isinstance(data, dict):
        csv_data = io.StringIO()
        writer = csv.writer(csv_data)
        writer.writerow(['user', 'endpoint'] + list(ReqRecord._fields))
        for (user, endpoint), req_data in data.items():
            writer.writerows([[user, endpoint] + list(i) for i in req_data])
        del writer
        csv_data.seek(0)
        text = csv_data.read()
    else:
        raise TypeError('Cannot convert type %s to CSV.' % type(data))

    response = make_response(text)
    response.headers["Content-Disposition"] = (
        "attachment; filename=%s" % name)
    return response


def make_download_link(my_request, updates, text='Download CSV'):
    """Helper function to make a download link to give request.

    :arg my_request:        A request object we are linking to.

    :arg updates:           A dict of parameters to override in my_request.

    :arg text='DownloadCSV':   Text string of download link.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :returns:   String representing HTML download link to request.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:    Make a simple download link to a request.

    """
    url_params = my_request.args.to_dict()
    url_params.update(updates)
    return '<A HREF="%s/%s?%s">%s</A>' % (
        my_request.url_root.rstrip('/'), my_request.path.lstrip('/'),
        urllib.parse.urlencode(url_params), text)
