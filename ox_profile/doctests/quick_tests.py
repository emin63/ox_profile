"""Some simple and quick tests to run.
"""

import doctest


def simple_doctest():
    """Simple test of whether things work.

>>> import time
>>> from threading import Timer
>>> from ox_profile.core import launchers
>>> launcher = launchers.SimpleLauncher()
>>> launcher.start()
>>> launcher.unpause()
>>> def boring(sleep=4):
...     if sleep <= 1:
...          print('getting unbored')
...          time.sleep(sleep)
...          return False
...     else:
...          print('bored for %.2f more seconds' % sleep)
...          time.sleep(1)
...          return boring(sleep - 1.0)
...
>>> boring()
bored for 4.00 more seconds
bored for 3.00 more seconds
bored for 2.00 more seconds
getting unbored
False
>>> launcher.is_alive()
True
>>> launcher.cancel()
>>> query, total_records = launcher.sampler.my_db.query()
>>> assert len(query) > 3
>>> print('Items in query:%c  - %s' % (10, ('%c  - '%10).join([
...     '%s: %s' % (i.name, i.hits) for i in query]))) # doctest: +ELLIPSIS
Items in query:
  - ...
>>> time.sleep(3)  # Give launcher time to die
>>> launcher.is_alive()
False
"""


if __name__ == '__main__':
    doctest.testmod()
    print('Finished Tests')
