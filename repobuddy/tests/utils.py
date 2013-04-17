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
import sys as _sys

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
        ShellHelper.make_dir(cls._utils_base_dir,
                             create_parent_dirs=True,
                             only_if_not_exists=True)
        return

    @classmethod
    def tearDownClass(cls):
        ShellHelper.remove_dir(cls._utils_base_dir)
        return

    def __init__(self, methodName='runTest'):
        super(UtilsTestCase, self).__init__(methodName)
        return

    def test_file_lock_multiple_times(self):
        lock_file = _os.path.join(type(self)._utils_base_dir, 'lock_acquire')
        with FileLock(lock_file) as first_lock:
            second_lock = FileLock(lock_file)
            with self.assertRaisesRegexp(
                    FileLockError,
                    r'^Timeout$') as err:
                second_lock.lock()
            self.assertTrue(err.exception.is_time_out)
        return


class UtilsTestSuite:
    @classmethod
    def get_test_suite(cls):
        tests = [
            'test_file_lock_multiple_times']
        return _unittest.TestSuite(map(UtilsTestCase, tests))
