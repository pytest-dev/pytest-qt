"""
Simple script to install PyQt or PySide in CI (Travis and AppVeyor).
"""
from __future__ import print_function
import os
import sys
import subprocess
import urllib


if 'APPVEYOR' in os.environ:
    def fix_registry(python_ver):
        """Update install path on windows registry so PyQt installation installs at the correct
        location.
        python_ver must be "34", "27", etc.
        """
        import _winreg as winreg
        python_dir = r'C:\Python%s' % python_ver
        print("Fixing registry %s..." % python_ver)
        assert os.path.isdir(python_dir)
        registry_key = r'Software\Python\PythonCore\%s.%s' % (python_ver[0], python_ver[1])
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            registry_key, 0,
                            winreg.KEY_WRITE) as key:
            winreg.SetValue(key, 'InstallPath', winreg.REG_SZ, python_dir)

    base_url = 'http://downloads.sourceforge.net/project/pyqt/'
    downloads = {
        'py34-pyqt5': 'PyQt5/PyQt-5.5/PyQt5-5.5-gpl-Py3.4-Qt5.5.0-x32.exe',
        'py35-pyqt5': 'PyQt5/PyQt-5.6/PyQt5-5.6-gpl-Py3.5-Qt5.6.0-x32-2.exe',
        'py34-pyqt4': 'PyQt4/PyQt-4.11.4/PyQt4-4.11.4-gpl-Py3.4-Qt4.8.7-x32.exe',
        'py27-pyqt4': 'PyQt4/PyQt-4.11.4/PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x32.exe',
    }
    if 'INSTALL_QT' in os.environ:
        fix_registry('35')
        caption = os.environ['INSTALL_QT']
        installers_dir = r'C:\Installers'
        if not os.path.isdir(installers_dir):
            os.makedirs(installers_dir)
        installer = os.path.join(installers_dir, 'install-%s.exe' % caption)
        if not os.path.isfile(installer):
            # download all files because the cache is for all builds
            for cap, url in sorted(downloads.items()):
                print("Downloading %s..." % cap)
                filename = os.path.join(installers_dir, 'install-%s.exe' % cap)
                urllib.urlretrieve(base_url + url, filename)
        else:
            print('Using cached installers')
        print('Installing %s...' % caption)
        subprocess.check_call([installer, '/S'])
        python = caption.split('-')[0]
        assert python[:2] == 'py'
        executable = r'C:\Python%s\python.exe' % python[2:]
        url = downloads[caption]
        module = url.split('/')[0]
        cmdline = [executable, '-c', 'import %s;print(%s)' % (module, module)]
        print('Checking: %r' % cmdline)
        subprocess.check_call(cmdline)
        print('OK')
    else:
        print('Skip install for this build')

elif 'TRAVIS' in os.environ:
    def apt_get_install(packages):
        print('Installing %s...' % ', '.join(packages))
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', '-qq'] + packages)

    py3k = sys.version_info[0] == 3
    pyqt_version = {'pyqt4': 4,
                    'pyqt4v2': 4,
                    'pyqt5': 5,
                    }
    if os.environ['PYTEST_QT_API'] in pyqt_version:
        pyqt_ver = pyqt_version[os.environ['PYTEST_QT_API']]
        if py3k:
            pkg = 'python3-pyqt%s' % pyqt_ver
        else:
            pkg = 'python-qt%s' % pyqt_ver
        apt_get_install([pkg])
    else:
        if py3k:
            pkg = 'python3-pyside'
        else:
            pkg = 'python-pyside'
        apt_get_install([pkg])

else:
    print('Nothing to do (not in Travis or AppVeyor)')
