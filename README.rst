Introduction
============

The ``ox_profile`` package provides a python framework for statistical
profiling. If you are using ``Flask``, then ``ox_profile`` provides a
flask blueprint so that you can start/stop/analyze profiling from within
your application. You can also run the profiler stand-alone without
``Flask`` as well.

To learn more, you can browse the overview slides in `PDF
form <https://github.com/emin63/ox_profile/blob/master/docs/overview_slides.pdf>`__
or read more details below.

Why statistical profiling (and why ox\_profile)?
================================================

Python contains many profilers which instrument your code and give you
exact results. A main benefit here is you know *exactly* what your
program is doing. The disadvantage is that there can be significant
overhead. With a statistical profiler such as ``ox_profile``, we sample
a running program periodically to get a sense of what the program is
doing with an overhead that can be tuned as desired.

One main use case for ``ox_profile`` specifically (and statistical
profiling in general) is that you can apply it to a production server to
see how things work "in the wild".

There are other statistical profilers out there for python (such as
statprof), which are pretty good and may be better for your needs than
``ox_profile``. So why would you consider ``ox_profile``? Some possible
reasons include:

1. Works on non-UNIX systems (e.g., works on Windows).

   -  Many other statistical profilers use various excellent features of
      LINUX or UNIX while ``ox_profile`` only really relies on the
      python ``sys._current_frames`` method.

2. Simple to understand.

   -  The code for ``ox_profile`` is fairly simple. The main work is
      really inside ``ox_profile.core.sampling.Sampler`` so it is easy
      to reason about or modify if you need slightly different
      profiling.

3. Flask Blueprint provided.

   -  If you are using Flask, then you can register the ``ox_profile``
      blueprint and easily get statistical profiling in your flask app.

Usage
=====

Stand alone
-----------

You can install ``ox_profile`` using pip via something like

.. code:: sh

        $ pip install ox_profile

The simplest way to run the profiler is by starting the launcher,
calling some functions, and the printing the profiled data via something
like:

::

        >>> from ox_profile.core.launchers import SimpleLauncher
        >>> profiler = SimpleLauncher.launch()      # Create and start a profiler.
        >>> # call some functions
        >>> print(profiler.show())                  # Print current results in preformated way.
        >>> profiler.cancel()                       # Turns off the profiler for good.

Often you may want a slightly more sophisticated use case where you can
pause and unpause the profiler and get more details about its status as
shown below:

::

        >>> from ox_profile.core import launchers
        >>> profiler = launchers.SimpleLauncher()    # Create an instance of launcher to be your profiler
        >>> profiler.start()                         # The profiler is a thread so we need to call start
        >>> profiler.unpause()                       # The profiler starts out paused so we unpause it
        >>> # call functions or start main program
        >>> profiler.pause()                         # You can pause if done profiling or leave running
        >>> query, total_records = profiler.query()  # Query for what the profiler has found
        >>> info = ['%s: %s' % (i.name, i.hits) for i in query]
        >>> print('Items in query:\n  - %s' % (('\n  - '.join(info))))
        >>> profiler.cancel()                        # This turns off the profiler for good

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
allowed to access ``ox_profile``. By default, we check
``current_user.name``, but you can set the ``OX_PROF_USERNAME_FIELD`` in
``app.config`` to something else (e.g., ``'email'`` to choose which
field of ``current_user`` is checked against the sequence of strings in
``OX_PROF_USERS``.

Pointing your browser to the route ``/ox_profile/status`` will then show
you the profiling status. By default, ``ox_profile`` starts out paused
so that it will not incur any overhead for your app. Go to the
``/ox_profile/unpause`` route to unpause and begin profiling so that
``/ox_profile/status`` shows something interesting.

Output
======

Currently ``ox_profile`` is in alpha mode and so the output is fairly
bare bones. When you look at the results of calling the ``query`` method
of an instance of ``SimpleLauncher`` in stand alone mode or at the
``/ox_profile/status`` route when running with flask, what you get is a
raw list of each function your program has called along with how many
times that function was called in our sampling.

Design
======

High Level Design
-----------------

Python offers a number of ways to get profiling information. In addition
to high-level profiling tools such as in the ``profile`` package, there
are specialized functions like ``sys.settrace`` and ``sys.setprofile``.
These are used for deterministic profiling and relatively robust but
have some overhead as they are invoked on each function call.

At a high level, we want a way to get a sample of what the python
interpreter is doing at any give instance. The sampling approach has the
advantage that by turning the sampling interval low enough, we can add
arbitrarily low overhead and make profiling feasible in a production
system. By taking a long enough sample, however, we should be able to
get arbitrarily accurate profiling information.

Low Level Design
----------------

At a low level, we do this sampling using ``sys._current_frames``. As
suggested by the leading underscore, this system function may be a bit
less robust. Indeed, the documentation says "This function should be
used for specialized purposes only." Hopefully the core python
developers will not make major changes to such a useful function.

In any case, the most interesting class is the ``Sampler`` class in the
``ox_profile.core.sampling`` module. This class has a run method which
does the following:

1. Uses ``sys.setswitchinterval`` to try and prevent a thread context
   switch.
2. Calls ``sys._current_frames`` to sample what the python interpreter
   is doing.
3. Updates a simple in-memory database of what functions are running.

In principle, you could just use the Sampler via something like

::

        >>> from ox_profile.core import sampling, recording
        >>> sampler = sampling.Sampler(recording.CountingRecorder())
        >>> def foo():
        ...     sampler.run()
        ...     return 'done'
        ... 
        >>> foo()

The above would have the sampler take a snapshot of the stack frames
when the ``foo`` function is run. Of course, this isn't very useful by
itself because it just tells you that ``foo`` is being run. It could be
useful if there were other threads which were running because the
sampler would tell you what stack frame those threads were in.

In principle, you could just call the ``Sampler.run`` method to track
other threads but that still isn't very convenient. To make things easy
to use, we provide the ``SimpleLauncher`` class in the
``ox_profile.core.launchers`` module as shown in the Usage section. The
``SimpleLauncher`` basically does the following:

1. Creates an instance of the ``Sampler`` class with reasonable
   defaults.
2. Initializes itself as a daemon thread and starts.
3. Pauses itself so the thread does nothing so as to not load the
   system.
4. Provides an ``unpause`` method you can use when you want to turn on
   profiling.
5. Provides a ``pause`` method if you want to turn off profiling.

In principle, you don't need much beyond the ``Sampler`` but the
``SimpleLauncher`` makes it easier to launch a ``Sampler`` in a separate
thread.

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
