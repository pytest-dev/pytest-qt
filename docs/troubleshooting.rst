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

GitHub Actions, Azure pipelines, Travis-CI and GitLab CI/CD
-----------------------------------------------------------

When using ``ubuntu-latest`` on Github Actions, the package ``libxkbcommon-x11-0`` has to be installed, ``DISPLAY`` should be set and ``xvfb`` run. More details can be found in issues `#293`_ and `#550`_.

.. _#293: https://github.com/pytest-dev/pytest-qt/issues/293
.. _#550: https://github.com/pytest-dev/pytest-qt/issues/550

Since Qt in version 5.15 ``xcb`` libraries are not distributed with Qt so this library in version at least 1.11 on runner. See more in https://codereview.qt-project.org/c/qt/qtbase/+/253905

Since Qt in version 6.5 ``xcb-cursor0`` is a requirement. See all Qt6 requirements in https://doc.qt.io/qt-6/linux-requirements.html

For GitHub Actions, Azure pipelines, Travis-CI and GitLab CI/CD you will need to install ``libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 x11-utils``

You might need to install ``libgl1 libegl1 libdbus-1-3`` as well.

As an example, here is a working Github Actions config :

.. code-block:: yaml

    name: my qt ci in github actions
    on: [push, pull_request]
    jobs:
      Linux:
        runs-on: ${{ matrix.os }}
        strategy:
          matrix:
            os : [ubuntu-latest]
            python: ["3.10"]
        env:
          DISPLAY: ':99.0'
        steps:
        - name: get repo
          uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: ${{ matrix.python }}
        - name: setup ${{ matrix.os }}
          run: |
            sudo apt install libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 x11-utils
            /sbin/start-stop-daemon --start --quiet --pidfile /tmp/custom_xvfb_99.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -screen 0 1920x1200x24 -ac +extension GLX

And here is a working Qt6 GitLab CI/CD config :

.. code-block:: yaml

    variables:
      DISPLAY: ':99.0'

    test:
      stage: test
      image: python:3.11
      script:
        - apt update
        - apt install -y libgl1 libegl1 libdbus-1-3 libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 x11-utils xvfb
        - /sbin/start-stop-daemon --start --quiet --pidfile /tmp/custom_xvfb_99.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -screen 0 1920x1200x24 -ac +extension GLX
        - python -m pip install pyqt6 pytest-qt

        - python -m pytest test.py


And here is a working Qt6 Azure Pipelines CI/CD config for ``ubuntu-latest`` :

.. code-block:: yaml

    # Set these environment variables for the job that runs tests

    variables:
      DISPLAY: ':99.0'  # This is needed for pytest-qt not to crash as mentioned above
      # Python fault handler is enabled in case UI tests crash without meaningful error messages
      PYTHONFAULTHANDLER: 'enabled'  # https://docs.python.org/3/library/faulthandler.html

    # Add this step to your CI pipeline before running your pytest-qt-based Qt6 tests with pytest

        # this was tested with ``ubuntu-latest`` image
        - script: |
            sudo apt update
            sudo apt-get install -y xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xinput0 libxcb-xfixes0 libxcb-shape0 libglib2.0-0 libgl1-mesa-dev
            sudo apt-get install -y '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
            sudo apt-get install -y x11-utils
            /sbin/start-stop-daemon --start --quiet --pidfile /tmp/custom_xvfb_99.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -screen 0 1920x1200x24 -ac +extension GLX
          displayName: 'Install and start xvfb and other dependencies on Linux for Qt GUI tests'
          condition: and(succeededOrFailed(), eq(variables['Agent.OS'], 'Linux'))

    # After this step, assuming you have ``pytest-qt`` installed, just run ``pytest`` and your PyQt6 tests will work


``tlambert03/setup-qt-libs``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Instead manually curate list of used packages you may use ``tlambert03/setup-qt-libs`` github action: https://github.com/tlambert03/setup-qt-libs

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
