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
    
    py_modules = ['distribute_setup'],
    
    # metadata for upload to PyPI
    author = "Bruno Oliveira",
    author_email = "nicoddemus@gmail.com",
    description = description,
    license = "LGPL",
    keywords = "pytest qt test unittest",
    url = "http://github.com/nicoddemus/pytest-qt",  
    classifiers=[
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ]
)