Troubleshooting
===============


InvocationError without further information
-------------------------------------------

``pytest-qt`` needs a DISPLAY to run. Otherwise Qt calls ``abort()``.
In this case no useful information can be given by ``pytest``, e.g.::

    ERROR: InvocationError:
    '/path/to/project/.tox/py36/bin/python setup.py test --addopts --doctest-modules'
    ___ summary _____
    ERROR: py36: commands failed

Recommended solution: use `pytest-xvfb`_.


Alternatively, ``tox`` users may edit ``tox.ini`` with::

    [testenv]
    passenv = DISPLAY XAUTHORITY


This has been found in `issue #170`_.

.. _pytest-xvfb: https://pypi.python.org/pypi/pytest-xvfb/
.. _issue #170: https://github.com/pytest-dev/pytest-qt/issues/170
