import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages
import pytestqt

description = "pytest plugin that adds fixtures for testing Qt (PyQt and PySide) applications."
setup(
    name = "pytest-qt",
    version = pytestqt.version,
    packages = ['pytestqt'],
    entry_points = {
        'pytest11' : ['pytest-qt = pytestqt.conftest'],
    },
    install_requires = ['pytest>=2.3.4'],
    
    # metadata for upload to PyPI
    author = "Bruno Oliveira",
    author_email = "nicoddemus@gmail.com",
    description = description,
    license = "LGPL",
    keywords = "pytest qt test unittest",
    url = "http://github.com/nicoddemus/pytest-qt",  
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: PyQt',
        'Framework :: PySide',
        'Framework :: Qt',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Desktop Environment :: Window Managers',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: User Interfaces',
    ]
)
