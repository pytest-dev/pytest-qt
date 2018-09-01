import sys

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


setup(
    name="pytest-qt",
    packages=["pytestqt"],
    entry_points={"pytest11": ["pytest-qt = pytestqt.plugin"]},
    install_requires=["pytest>=2.7.0"],
    extras_require={"doc": ["sphinx", "sphinx_rtd_theme"]},
    # metadata for upload to PyPI
    author="Bruno Oliveira",
    author_email="nicoddemus@gmail.com",
    description="pytest support for PyQt and PySide applications",
    long_description=open("README.rst").read(),
    license="MIT",
    keywords="pytest qt test unittest",
    url="http://github.com/pytest-dev/pytest-qt",
    use_scm_version={"write_to": "pytestqt/_version.py"},
    setup_requires=["setuptools_scm"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Desktop Environment :: Window Managers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: User Interfaces",
    ],
    tests_require=["pytest"],
    cmdclass={"test": PyTest},
)
