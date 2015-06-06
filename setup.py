import sys
import re

from setuptools import setup
from setuptools.command.test import test as TestCommand


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


with open('pytestqt/__init__.py') as f:
    m = re.search("version = '(.*)'", f.read())
    assert m is not None
    version = m.group(1)

setup(
    name="pytest-qt",
    version=version,
    packages=['pytestqt'],
    entry_points={
        'pytest11': ['pytest-qt = pytestqt.plugin'],
    },
    install_requires=['pytest>=2.7.0'],

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
