from setuptools import setup
import pytestqt


setup(
    name="pytest-qt",
    version=pytestqt.version,
    packages=['pytestqt', 'pytestqt._tests'],
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
    url="http://github.com/nicoddemus/pytest-qt",
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
    ]
)
