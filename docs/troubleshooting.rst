Troubleshooting
===============


tox: ``InvocationError`` without further information
----------------------------------------------------

It might happen that your ``tox`` run finishes abruptly without any useful information, e.g.::

    ERROR: InvocationError:
    '/path/to/project/.tox/py36/bin/python setup.py test --addopts --doctest-modules'
    ___ summary _____
    ERROR: py36: commands failed

``pytest-qt`` needs a ``DISPLAY`` to run, otherwise ``Qt`` calls ``abort()`` and the process crashes immediately.

One solution is to use the `pytest-xvfb`_ plugin which takes care of the grifty details automatically, starting up a virtual framebuffer service, initializing variables, etc. This is the recommended solution if you are running in CI servers without a GUI, for example in Travis or CircleCI.

Alternatively, ``tox`` users may edit ``tox.ini`` to allow the relevant variables to be passed to the underlying
``pytest`` invocation:

.. code-block:: ini

    [testenv]
    passenv = DISPLAY XAUTHORITY

Note that this solution will only work in boxes with a GUI.

More details can be found in `issue #170`_.

.. _pytest-xvfb: https://pypi.python.org/pypi/pytest-xvfb/
.. _issue #170: https://github.com/pytest-dev/pytest-qt/issues/170



xvfb: ``AssertionError``, ``TimeoutError`` when using ``waitUntil``, ``waitExposed`` and UI events.
---------------------------------------------------------------------------------------------------

When using ``xvfb`` or equivalent make sure to have a window manager running otherwise UI events will not work properly.

If you are running your code on Travis-CI make sure that your ``.travis.yml`` has the following content:

.. code-block:: yaml

    sudo: required

    before_install:
      - sudo apt-get update
      - sudo apt-get install -y xvfb herbstluftwm

    install:
      - "export DISPLAY=:99.0"
      - "/sbin/start-stop-daemon --start --quiet --pidfile /tmp/custom_xvfb_99.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset"
      - sleep 3

    before_script:
      - "herbstluftwm &"
      - sleep 1

More details can be found in `issue #206`_.

.. _issue #206: https://github.com/pytest-dev/pytest-qt/issues/206
