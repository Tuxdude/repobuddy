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
import re as _re
import shlex as _shlex
import sys as _sys
import threading as _threading
import time as _time

if _sys.version_info < (2, 7):
    import unittest2 as _unittest   # pylint: disable=F0401
else:
    import unittest as _unittest    # pylint: disable=F0401


from repobuddy.arg_parser import ArgParser, ArgParserError
from repobuddy.tests.common import ShellHelper, TestCaseBase, TestCommon, \
    TestSuiteManager
from repobuddy.globals import HelpStrings
from repobuddy.utils import Logger
from repobuddy.version import __version__


class ArgParserTestCase(TestCaseBase):
    @classmethod
    def setUpClass(cls):
        cls._test_base_dir = TestSuiteManager.get_base_dir()
        return

    @classmethod
    def tearDownClass(cls):
        return

    def _hook_into_logger(self):
        self._str_stream = TestCommon.get_string_stream()
        Logger.msg_stream = self._str_stream
        Logger.error_stream = self._str_stream
        return

    def _reset_logger(self):
        Logger.msg_stream = self._original_logger_state['msg_stream']
        Logger.error_stream = self._original_logger_state['error_stream']
        return

    def _test_help(self, args_str):
        self._hook_into_logger()
        arg_parser = ArgParser(self._handlers)
        with self.assertRaisesRegexp(ArgParserError, None) as err:
            arg_parser.parse(_shlex.split(args_str))
        self.assertTrue(err.exception.exit_prog_without_error)

        help_regex = _re.compile(
            r'^usage: ([a-z]+) ((\[-(h|v)\] ){2})\{(([a-z]+,)*[a-z]+)\} ' +
            r'\.\.\.\s+' + HelpStrings.PROGRAM_DESCRIPTION + '\s+')
        match_obj = help_regex.search(self._str_stream.getvalue())
        self.assertIsNotNone(match_obj)
        groups = match_obj.groups()

        self.assertEqual(groups[0], 'repobuddy')
        self._assert_count_equal(groups[1].rstrip().split(' '),
                                 ['[-h]', '[-v]'])
        self._assert_count_equal(groups[4].rstrip().split(','),
                                 ['status', 'init', 'help'])
        return

    def _test_version(self, args_str):
        self._hook_into_logger()
        arg_parser = ArgParser(self._handlers)
        with self.assertRaisesRegexp(ArgParserError, None) as err:
            arg_parser.parse(_shlex.split(args_str))
        self.assertTrue(err.exception.exit_prog_without_error)
        self.assertEqual(self._str_stream.getvalue().rstrip(), __version__)
        return

    def __init__(self, methodName='runTest'):
        super(ArgParserTestCase, self).__init__(methodName)
        self._original_logger_state = {'msg_stream': Logger.msg_stream,
                                       'error_stream': Logger.error_stream}
        self._handlers = {}
        self._str_stream = TestCommon.get_string_stream()
        return

    def setUp(self):
        self._handlers.clear()
        self._handlers['init'] = None
        self._handlers['status'] = None

        self._set_tear_down_cb(self._reset_logger)
        return

    def test_help(self):
        self._test_help('-h')
        self._test_help('--help')
        return

    def test_version(self):
        self._test_version('-v')
        self._test_version('--version')
        return


class ArgParserTestSuite:  # pylint: disable=W0232
    @classmethod
    def get_test_suite(cls):
        tests = [
            'test_help',
            'test_version']
        return _unittest.TestSuite(map(ArgParserTestCase, tests))