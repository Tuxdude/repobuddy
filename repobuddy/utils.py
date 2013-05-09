#
#   Copyright (C) 2013 Ash (Tuxdude) <tuxdude.github@gmail.com>
#
#   This file is part of repobuddy.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
.. module: repobuddy.utils
   :platform: Unix, Windows
   :synopsis: Utility classes used by the rest of ``repobuddy``.
.. moduleauthor: Ash <tuxdude.github@gmail.com>

"""

import errno as _errno
import os as _os
import pkg_resources as _pkg_resources
import sys as _sys
import time as _time


class RepoBuddyBaseException(Exception):

    """Base class of all exceptions in ``repobuddy``."""

    def __init__(self, error_str):
        """Initializer.

        :param error_str: The error string to store in the exception.
        :type error_str: str

        """
        super(RepoBuddyBaseException, self).__init__(error_str)
        self._error_str = str(error_str)
        return

    def __str__(self):
        return self._error_str

    def __repr__(self):
        return self._error_str


class FileLockError(RepoBuddyBaseException):

    """Exception raised by :class:`FileLock`.

    :ivar is_time_out: Set to ``True`` if a timeout occurred when trying to
        acquire the lock, ``False`` otherwise.

    """

    def __init__(self, error_str, is_time_out=False):
        """Initializer.

        :param error_str: The error string to store in the exception.
        :type error_str: str
        :param is_time_out: If ``True``, the error is because of a timeout in
            acquiring the lock. The ``is_time_out`` instance variable in the
            exception object is set to this value.

        """
        super(FileLockError, self).__init__(error_str)
        self.is_time_out = is_time_out
        return


# Credits to Evan for the FileLock code
# noqa http://www.evanfosmark.com/2009/01/cross-platform-file-locking-support-in-python/ # pylint: disable=C0301
# Have made minor changes to the original version
class FileLock(object):

    """A mutual exclusion primitive using lock files."""

    def __init__(self, file_name, timeout=1, delay=.1):
        """Initializer.

        :param file_name: Name of the lock file to be created. Filename can be
            either an absolute or a relative file path.
        :type file_name: str
        :param timeout: Maxium time in seconds until :meth:`acquire()` blocks
            in trying to acquire the lock.
            If ``timeout`` seconds have elapsed without
            successfully acquiring the lock, :exc:`FileLockError` is raised.
        :type timeout: float
        :param delay: Time interval in seconds between 2 successive lock
            attempts.
        :type delay: float

        """
        self._is_locked = False
        self._lock_file = _os.path.join(file_name)
        self._timeout = timeout
        self._delay = delay
        self._fd = None
        return

    def __del__(self):
        self.release()
        return

    def __enter__(self):
        if not self._is_locked:
            self.acquire()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self._is_locked:
            self.release()
        return

    def acquire(self):
        """Acquire the lock.

        Acquires the lock within the designated ``timeout``, failing
        which it raises :exc:`FileLockError` with ``is_time_out`` set to
        ``True``.

        :returns: None
        :raises: :exc:`FileLockError` on errors. ``is_time_out`` is set to
            ``True`` only if the designated ``timeout`` has elapsed.

        """
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

    def release(self):
        """Release the lock.

        :returns: None
        :raises: :exc:`FileLockError` on errors. If the lock file has already
            been deleted, no exception is raised.

        """
        if self._is_locked:
            _os.close(self._fd)
            try:
                _os.unlink(self._lock_file)
            except OSError as err:
                # Lock file could be deleted, ignoring
                if err.errno != _errno.ENOENT:
                    raise FileLockError('Error: ' + str(err))
            self._is_locked = False
        return


class ResourceHelperError(RepoBuddyBaseException):

    """Exception raised by :class:`ResourceHelper`."""

    def __init__(self, error_str):
        """Initializer.

        :param error_str: The error string to store in the exception.
        :type error_str: str

        """
        super(ResourceHelperError, self).__init__(error_str)
        return


class ResourceHelper:   # pylint: disable=W0232

    """A helper class for loading resources."""

    @classmethod
    def open_data_file(cls, package_name, file_name):
        """Get a stream handle to the resource.

        :param package_name: Package name to fetch the resource from.
        :type package_name: str
        :param file_name: Filename of the resource.
        :type file_name: str
        :returns: A stream object representing the resource file.
        :raises: :exc:`ResourceHelperError` if unable to locate the resource
            ``file_name`` in ``package_name``.

        """
        if _pkg_resources.resource_exists(package_name, file_name):
            return _pkg_resources.resource_stream(package_name, file_name)
        else:
            raise ResourceHelperError(
                'Unable to locate the resource: %s in package %s' %
                (file_name, package_name))
        return


class EqualityBase(object):

    """Rrovides equality comparison operations.

    A base class which provides support for performing equality comparison
    on the instance. The type and the instance dictionary are used for
    comparison.

    """

    def __eq__(self, other):
        return (type(other) is type(self)) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class LoggerError(Exception):

    """Exception raised by :class:`Logger`."""

    def __init__(self, error_str):
        """Initializer.

        :param error_str: The error string to store in the exception.
        :type error_str: str

        """
        super(LoggerError, self).__init__(error_str)
        self._error_str = error_str
        return

    def __str__(self):
        return str(self._error_str)

    def __repr__(self):
        return str(self._error_str)


class Logger:   # pylint: disable=W0232

    """Provides logging support for the rest of ``repobuddy``.

    Currently supported log levels are:

    -   DEBUG
    -   MESSAGE
    -   ERROR

    """

    disable_debug = True
    debug_stream = _sys.stdout
    msg_stream = _sys.stdout
    error_stream = _sys.stdout

    def __new__(cls):
        raise LoggerError('This class should not be instantiated')

    @classmethod
    def msg(cls, msg, append_new_line=True):
        """Add a log entry of level ``MESSAGE``.

        :param msg: The message to log.
        :type msg: str
        :param append_new_line: Appends a new line after the log message when
            set to ``True``.
        :type append_new_line: Boolean
        :returns: None
        :raises: :exc:`LoggerError` on errors.

        """
        if append_new_line:
            cls.msg_stream.write(msg + '\n')
        else:
            cls.msg_stream.write(msg)
        return

    @classmethod
    def debug(cls, msg, append_new_line=True):
        """Add a log entry of level ``DEBUG``.

        :param msg: The message to log.
        :type msg: str
        :param append_new_line: Appends a new line after the log message when
            set to ``True``.
        :type append_new_line: Boolean
        :returns: None
        :raises: :exc:`LoggerError` on errors.

        """
        if not cls.disable_debug:
            if append_new_line:
                cls.debug_stream.write(msg + '\n')
            else:
                cls.debug_stream.write(msg)
        return

    @classmethod
    def error(cls, msg, append_new_line=True):
        """Add a log entry of level ``ERROR``.

        :param msg: The message to log.
        :type msg: str
        :param append_new_line: Appends a new line after the log message when
            set to ``True``.
        :type append_new_line: Boolean
        :returns: None
        :raises: :exc:`LoggerError` on errors.

        """
        if append_new_line:
            cls.error_stream.write(msg + '\n')
        else:
            cls.error_stream.write(msg)
        return
