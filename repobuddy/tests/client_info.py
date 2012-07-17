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
import unittest as _unittest

from repobuddy.tests.common import ShellHelper, TestCommon, TestCaseBase
from repobuddy.utils import ResourceHelper


class ClientInfoTestCase(TestCaseBase):
    @classmethod
    def setUpClass(cls):
        return

    @classmethod
    def tearDownClass(cls):
        return

    def __init__(self, methodName='runTest'):
        super(ClientInfoTestCase, self).__init__(methodName)
        return

    def test_invalid_file(self):
        return


class ClientInfoTestSuite:
    @classmethod
    def get_test_suite(cls):
        tests = ['test_invalid_file']
        return _unittest.TestSuite(map(ClientInfoTestCase, tests))
