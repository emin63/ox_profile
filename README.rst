Introduction
============

The ``ox_profile`` package provides a python framework for statistical
profiling. If you are using ``Flask``, then ``ox_profile`` provides a
flask blueprint so that you can start/stop/analyze profiling from within
your application. You can also run the profiler stand-alone without
``Flask`` as well.

Why statistical profiling?
==========================

Python contains many profilers which instrument your code and give you
exact results. A main benefit here is you know *exactly* what your
program is doing. The disadvantage is that there can be significant
overhead. With a statistical profiler such as ``ox_profile``, we sample
a running program periodically to get a sense of what the program is
doing with an overhead that can be tuned as desired.

One main use case for ``ox_profile`` specifically (and statistical
profiling in general) is that you can apply it to a production server to
see how things work "in the wild".

Usage
=====

With Flask
----------

If you are using the python flask framework and have installed
``ox_profile`` (e.g., with ``pip install ox_profile``) then you can
simply do the following in the appropriate place after initializing your
app:

::

        from ox_profile.ui.flask.views import OX_PROF_BP
        app.register_blueprint(OX_PROF_BP)
        app.config['OX_PROF_USERS'] = {<admin_user_1>, <admin_user_2>, ...}

where ``<admin_user_>``, etc. are strings referring to users who are
allowed to access ``ox_profile``.

Pointing your browser to the route ``/ox_profile/status`` will then show
you the profiling status. By default, ``ox_profile`` starts out paused
so that it will not incur any overhead for your app. Go to the
``/ox_profile/unpause`` route to unpause and begin profiling so that
``/ox_profile/status`` shows something interesting.

Stand alone
-----------

You can run the profiler without flask simply by starting the launcher
and then running queries when convenient via something like:

::

        >>> from ox_profile.core import launchers
        >>> launcher = launchers.SimpleLauncher()
        >>> launcher.start()
        >>> launcher.unpause()
        >>> <call some functions>
        >>> query, total_records = launcher.sampler.my_db.query()
        >>> info = ['%s: %s' % (i.name, i.hits) for i in query]
        >>> print('Items in query:\n  - %s' % (('\n  - '.join(info))))
        >>> launcher.cancel()  # This turns off the profiler for good

Output
======

Currently ``ox_profile`` is in alpha mode and so the output is fairly
bare bones. When you look at the results of
``launcher.sampler.my_db.query()`` in stand alone mode or at the
``/ox_profile/status`` route when running with flask, what you get is a
raw list of each function your program has called along with how many
times that function was called in our sampling.

Known Issues
============

Granularity
-----------

With statistical profiling, we need to ask the thread to sleep for some
small amount so that it does not overuse CPU resources. Sadly, the
minimum sleep time (using either ``time.sleep`` or ``wait`` on a thread
event) is on the order of 1--10 milliseconds on most operating systems.
This means that you can not efficiently do statistical profiling at a
granularity finer than about 1 millisecond.

Thus you should consider statistical profiling as a tool to find the
relatively slow issues in production and not a tool for optimizing
issues faster than about a millisecond.
