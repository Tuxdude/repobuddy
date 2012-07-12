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

import unittest as _unittest
import inspect as _inspect

from repobuddy.utils import Logger


class GitWrapperTestCase(_unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Logger.msg('%s %s' % (cls.__name__,
                              _inspect.stack()[0][3]))
        return

    @classmethod
    def tearDownClass(cls):
        Logger.msg('%s %s' % (cls.__name__,
                              _inspect.stack()[0][3]))
        return

    def setUp(self):
        Logger.msg('%s %s' % (self.__class__.__name__,
                              _inspect.stack()[0][3]))
        return

    def tearDown(self):
        Logger.msg('%s %s' % (self.__class__.__name__,
                              _inspect.stack()[0][3]))
        return

    def test_clone(self):
        Logger.msg('%s %s' % (self.__class__.__name__,
                              _inspect.stack()[0][3]))
        self.assertEqual(1, 1, 'Value mismtach')
        return


class GitWrapperTestSuite():
    def __init__(self):
        return

    def get_test_suite(self):
        tests = ['test_clone']
        return _unittest.TestSuite(map(GitWrapperTestCase, tests))


def setUpModule():
    Logger.msg('%s %s' % (__name__,
                          _inspect.stack()[0][3]))
    return


def tearDownModule():
    Logger.msg('%s %s' % (__name__,
                          _inspect.stack()[0][3]))
    return
