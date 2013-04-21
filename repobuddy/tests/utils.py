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

import os as _os
import shlex as _shlex
import sys as _sys
import threading as _threading
import time as _time

if _sys.version_info < (2, 7):
    import unittest2 as _unittest   # pylint: disable=F0401
else:
    import unittest as _unittest    # pylint: disable=F0401


from repobuddy.utils import FileLock, FileLockError
from repobuddy.tests.common import ShellHelper, TestCaseBase, TestSuiteManager


class UtilsTestCase(TestCaseBase):
    @classmethod
    def setUpClass(cls):
        cls._test_base_dir = TestSuiteManager.get_base_dir()
        cls._utils_base_dir = _os.path.join(cls._test_base_dir, 'utils')
        ShellHelper.remove_dir(cls._utils_base_dir)
        ShellHelper.make_dir(cls._utils_base_dir,
                             create_parent_dirs=True,
                             only_if_not_exists=True)
        return

    @classmethod
    def tearDownClass(cls):
        ShellHelper.remove_dir(cls._utils_base_dir)
        return

    def _wait_with_lock(self, file_name, event):
        with FileLock(file_name):
            event.wait()
        return

    def __init__(self, methodName='runTest'):
        super(UtilsTestCase, self).__init__(methodName)
        return

    def test_file_lock_basic(self):
        lock_file = _os.path.join(type(self)._utils_base_dir,
                                  'lock_basic')
        with FileLock(lock_file):
            self.assertTrue(_os.path.isfile(lock_file))
        self.assertFalse(_os.path.isfile(lock_file))
        return

    def test_file_lock_multiple_times(self):
        lock_file = _os.path.join(type(self)._utils_base_dir,
                                  'lock_multi_times')
        with FileLock(lock_file):
            second_lock = FileLock(lock_file)
            with self.assertRaisesRegexp(
                    FileLockError,
                    r'^Timeout$') as err:
                second_lock.acquire()
            self.assertTrue(err.exception.is_time_out)
        return

    def test_file_lock_multiple_threads(self):
        lock_file = _os.path.join(type(self)._utils_base_dir,
                                  'lock_multi_thread')
        event = _threading.Event()
        event.clear()
        wait_thread = _threading.Thread(target=self._wait_with_lock,
                                        args=(lock_file, event))
        self._set_tear_down_cb(event.set)
        wait_thread.daemon = False
        lock = FileLock(lock_file)

        with self.assertRaisesRegexp(
                FileLockError,
                r'^Timeout$') as err:
            wait_thread.start()
            _time.sleep(3)
            lock.acquire()
        self.assertTrue(err.exception.is_time_out)

        event.set()
        wait_thread.join(3)
        self.assertFalse(wait_thread.is_alive())

        lock.acquire()
        lock.release()
        return

    def test_file_lock_delete_with_acquire(self):
        lock_file = _os.path.join(type(self)._utils_base_dir,
                                  'lock_delete_with_acquire')
        with FileLock(lock_file):
            self.assertTrue(_os.path.isfile(lock_file))
            ShellHelper.remove_file(lock_file)

            second_lock = FileLock(lock_file)
            second_lock.acquire()
            second_lock.release()

        self.assertFalse(_os.path.isfile(lock_file))
        return

    def test_file_lock_dir_without_permissions(self):
        base_dir = type(self)._utils_base_dir
        test_dir = _os.path.join(base_dir,
                                 'test-permissions')
        ShellHelper.make_dir(test_dir,
                             create_parent_dirs=True,
                             only_if_not_exists=True)
        ShellHelper.exec_command(
            _shlex.split('sudo chown root:root ' + test_dir), base_dir)
        self._set_tear_down_cb(ShellHelper.exec_command,
                               _shlex.split('sudo rm -rf ' + test_dir),
                               base_dir)
        lock_file = _os.path.join(test_dir, 'lock_no_permissions')
        lock_handle =  FileLock(lock_file)

        with self.assertRaisesRegexp(
                FileLockError,
                r'^Error: Unable to create the lock file: ' +
                r'.*lock_no_permissions$'):
            lock_handle.acquire()
        return


class UtilsTestSuite:  # pylint: disable=W0232
    @classmethod
    def get_test_suite(cls):
        tests = [
            'test_file_lock_basic',
            'test_file_lock_multiple_times',
            'test_file_lock_multiple_threads',
            'test_file_lock_delete_with_acquire',
            'test_file_lock_dir_without_permissions']
        return _unittest.TestSuite(map(UtilsTestCase, tests))
