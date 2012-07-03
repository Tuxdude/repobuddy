#
#   Copyright (C) 2012 Ash (Tuxdude) <tuxdude.github@gmail.com>
#
#   This file is part of repobuddy.
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as
#   published by the Free Software Foundation; either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.
#

import errno as _errno
import os as _os
import sys as _sys
import time as _time

class FileLockError(Exception):
    def __init__(self, errorStr, isTimeOut = False):
        self._errorStr = errorStr
        self.isTimeOut = isTimeOut
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return str(self._errorStr)

# Credits to Evan for the FileLock code
# http://www.evanfosmark.com/2009/01/cross-platform-file-locking-support-in-python/
# Have made minor changes to the original version
class FileLock(object):
    def __init__(self, fileName, timeout = 1, delay = .1):
        self._isLocked = False
        self._lockFile = _os.path.join(fileName)
        self._timeout = timeout
        self._delay = delay
        return

    def __del__(self):
        self.unlock()
        return

    def __enter__(self):
        if not self._isLocked:
            self.lock()
        return self

    def __exit__(self, exceptionType, exceptionValue, traceback):
        if self._isLocked:
            self.unlock()
        return

    def lock(self):
        begin = _time.time()
        while True:
            try:
                self._fd = _os.open(self._lockFile, _os.O_CREAT | _os.O_EXCL | _os.O_RDWR)
                break
            except OSError as err:
                if err.errno != _errno.EEXIST:
                    raise FileLockError(
                            'Error: Unable to create the lock file: ' +
                            self._lockFile)
                if (_time.time() - begin) >= self._timeout:
                    raise FileLockError(
                            'Timeout',
                            isTimeOut = True)
            _time.sleep(self._delay)
        self._isLocked = True
        return

    def unlock(self):
        if self._isLocked:
            _os.close(self._fd)
            _os.unlink(self._lockFile)
            self._isLocked = False
        return

class Logger:
    @classmethod
    def Msg(cls, msg, appendNewLine = True):
        if appendNewLine:
            _sys.stdout.write(msg + '\n')
        else:
            _sys.stdout.write(msg)
        return

    # TODO: Add a way to turn on/off the debug outputs
    @classmethod
    def Debug(cls, msg, appendNewLine = True):
        if appendNewLine:
            _sys.stdout.write(msg + '\n')
        else:
            _sys.stdout.write(msg)
        return

    @classmethod
    def Error(cls, msg, appendNewLine = True):
        if appendNewLine:
            _sys.stdout.write(msg + '\n')
        else:
            _sys.stdout.write(msg)
        return

