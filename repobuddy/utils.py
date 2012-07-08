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
    def __init__(self, error_str, is_time_out=False):
        super(FileLockError, self).__init__(error_str)
        self._error_str = error_str
        self.is_time_out = is_time_out
        return

    def __str__(self):
        return str(self._error_str)

    def __repr__(self):
        return str(self._error_str)


# Credits to Evan for the FileLock code
# http://www.evanfosmark.com/2009/01/cross-platform-file-locking-support-in-python/
# Have made minor changes to the original version
class FileLock(object):
    def __init__(self, file_name, timeout=1, delay=.1):
        self._is_locked = False
        self._lock_file = _os.path.join(file_name)
        self._timeout = timeout
        self._delay = delay
        self._fd = None
        return

    def __del__(self):
        self.unlock()
        return

    def __enter__(self):
        if not self._is_locked:
            self.lock()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self._is_locked:
            self.unlock()
        return

    def lock(self):
        begin = _time.time()
        while True:
            try:
                self._fd = _os.open(
                    self._lock_file,
                    _os.O_CREAT | _os.O_EXCL | _os.O_RDWR)
                break
            except OSError as err:
                if err.errno != _errno.EEXIST:
                    raise FileLockError(
                        'Error: Unable to create the lock file: ' +
                        self._lock_file)
                if (_time.time() - begin) >= self._timeout:
                    raise FileLockError(
                        'Timeout',
                        is_time_out=True)
            _time.sleep(self._delay)
        self._is_locked = True
        return

    def unlock(self):
        if self._is_locked:
            _os.close(self._fd)
            _os.unlink(self._lock_file)
            self._is_locked = False
        return


class LoggerError(Exception):
    def __init__(self, error_str):
        super(LoggerError, self).__init__(error_str)
        self._error_str = error_str
        return

    def __str__(self):
        return str(self._error_str)

    def __repr__(self):
        return str(self._error_str)


class Logger:
    _disable_debug = True

    def __new__(cls):
        raise LoggerError('This class should not be instantiated')

    @classmethod
    def msg(cls, msg, append_new_line=True):
        if append_new_line:
            _sys.stdout.write(msg + '\n')
        else:
            _sys.stdout.write(msg)
        return

    @classmethod
    def debug(cls, msg, append_new_line=True):
        if not cls._disable_debug:
            if append_new_line:
                _sys.stdout.write(msg + '\n')
            else:
                _sys.stdout.write(msg)
        return

    @classmethod
    def error(cls, msg, append_new_line=True):
        if append_new_line:
            _sys.stdout.write(msg + '\n')
        else:
            _sys.stdout.write(msg)
        return
