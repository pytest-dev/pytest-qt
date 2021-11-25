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

GitHub Actions
----------------

When using ``ubuntu-latest`` on Github Actions, the package ``libxkbcommon-x11-0`` has to be installed, ``DISPLAY`` should be set and ``xvfb`` run. More details can be found in `issue #293`_.

.. _issue #293: https://github.com/pytest-dev/pytest-qt/issues/293

Since Qt in version 5.15 ``xcb`` libraries are not distributed with Qt so this library in version at least 1.11 on runner. See more in https://codereview.qt-project.org/c/qt/qtbase/+/253905

For Github Actions, Azure pipelines and Travis-CI you will need to install ``libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0``

As an example, here is a working config :

.. code-block:: yaml

    name: my qt ci in github actions
    on: [push, pull_request]
    jobs:
      Linux:
        runs-on: ${{ matrix.os }}
        strategy:
          matrix:
            os : [ubuntu-latest]
            python: [3.7]
        env:
          DISPLAY: ':99.0'
        steps:
        - name: get repo
          uses: actions/checkout@v1
        - name: Set up Python
          uses: actions/setup-python@v1
          with:
            python-version: ${{ matrix.python }}
        - name: setup ${{ matrix.os }}
          run: |
            sudo apt install libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0
            /sbin/start-stop-daemon --start --quiet --pidfile /tmp/custom_xvfb_99.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -screen 0 1920x1200x24 -ac +extension GLX

pytest-xvfb
~~~~~~~~~~~

Instead of running Xvfb manually it is possible to use ``pytest-xvfb`` plugin.

Using with other Qt-related packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Python's Qt modules (``PySide`` or ``PyQt5``) with other packages which
use Qt (e.g. ``cv2``) can result in conflicts. This is because the latter builds
their own Qt and modify Qt-related environment variables. This may not raise errors
in your local app, but running the tests on CI servers can fail.

In this case, try use the package without Qt dependency. For example, if your
code does not rely on ``cv2``'s Qt feature you can use
``opencv-python-headless`` instead of full ``opencv-python``.

More details can be found in `issue #396`_.

.. _issue #396: https://github.com/pytest-dev/pytest-qt/issues/396
