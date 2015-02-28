import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import pytestqt


class PyTest(TestCommand):
    """
    Overrides setup "test" command, taken from here:
    http://pytest.org/latest/goodpractises.html
    """

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main([])
        sys.exit(errno)


setup(
    name="pytest-qt",
    version=pytestqt.version,
    packages=['pytestqt'],
    entry_points={
        'pytest11': ['pytest-qt = pytestqt.plugin'],
    },
    install_requires=['pytest>=2.3.4'],

    # metadata for upload to PyPI
    author="Bruno Oliveira",
    author_email="nicoddemus@gmail.com",
    description='pytest support for PyQt and PySide applications',
    long_description=open('README.rst').read(),
    license="LGPL",
    keywords="pytest qt test unittest",
    url="http://github.com/pytest-dev/pytest-qt",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Desktop Environment :: Window Managers',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: User Interfaces',
    ],
    tests_requires=['pytest'],
    cmdclass={'test': PyTest},
)
