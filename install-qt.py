'''
Simple script to install PyQt or PySide based on PYTEST_QT_FORCE_PYQT
and python version. Meant to be used in travis-ci.
'''
import os
import sys

def run(cmd):
    print(cmd)
    r = os.system(cmd)
    if r != 0:
        sys.exit('command %s failed with status %s' % (cmd, r))

py3k = sys.version_info[0] == 3
if os.environ['PYTEST_QT_API'] in ('pyqt4', 'pyqt5'):
    pyqt_ver = os.environ['PYTEST_QT_API'][-1]
    if py3k:
        run('sudo apt-get install -qq python3-pyqt%s{,-dbg}' % pyqt_ver)
    else:
        run('sudo apt-get install -qq python-qt%s{,-dbg}' % pyqt_ver)
else:
    if py3k:
        run('sudo apt-get install -qq python3-pyside{,-dbg}')
    else:
        run('sudo apt-get install -qq python-pyside')

