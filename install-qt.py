'''
Simple script to install PyQt or PySide based on PYTEST_QT_FORCE_PYQT
and python version. Meant to be used in travis-ci.
'''
import os
import sys
import subprocess


def install(packages):
    print('Installing %s...' % ', '.join(packages))
    subprocess.check_call(['sudo', 'apt-get', 'install', '-qq'] + packages)

py3k = sys.version_info[0] == 3
if os.environ['PYTEST_QT_API'] in ('pyqt4', 'pyqt5'):
    pyqt_ver = os.environ['PYTEST_QT_API'][-1]
    if py3k:
        pkg = 'python3-pyqt%s' % pyqt_ver
    else:
        pkg = 'python-qt%s' % pyqt_ver
    install([pkg, pkg + '-dbg'])
else:
    if py3k:
        pkg = 'python3-pyside'
    else:
        pkg = 'python-pyside'
    install([pkg])
