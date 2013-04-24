#
#   Copyright (C) 2013 Ash (Tuxdude) <tuxdude.github@gmail.com>
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

import re as _re
import shlex as _shlex
import sys as _sys

if _sys.version_info < (2, 7):
    import unittest2 as _unittest   # pylint: disable=F0401
else:
    import unittest as _unittest    # pylint: disable=F0401


from repobuddy.arg_parser import ArgParser, ArgParserError
from repobuddy.tests.common import TestCaseBase, TestCommon, TestSuiteManager
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
        self._set_tear_down_cb(self._reset_logger)
        return

    def _reset_logger(self):
        Logger.msg_stream = self._original_logger_state['msg_stream']
        Logger.error_stream = self._original_logger_state['error_stream']
        return

    def _reset_handlers(self):
        self._last_handler = None
        self._last_handler_args.clear()
        self._handlers.clear()
        self._handlers['init'] = None
        self._handlers['status'] = None
        return

    def _test_help(self, args_str):
        self._hook_into_logger()
        arg_parser = ArgParser(self._handlers)
        with self.assertRaisesRegexp(ArgParserError, None) as err:
            arg_parser.parse(_shlex.split(args_str))
        self.assertTrue(err.exception.exit_prog_without_error)

        usage_regex = _re.compile(
            r'^usage: ([a-z]+) ((\[-(h|v)\] ){2})\{(([a-z]+,)*[a-z]+)\} ' +
            r'\.\.\.\s+' + HelpStrings.PROGRAM_DESCRIPTION + '\s+')
        match_obj = usage_regex.search(self._str_stream.getvalue())
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

    def _test_init_help(self, args_str):
        self._hook_into_logger()
        arg_parser = ArgParser(self._handlers)
        with self.assertRaisesRegexp(ArgParserError, None) as err:
            arg_parser.parse(_shlex.split(args_str))
        self.assertTrue(err.exception.exit_prog_without_error)

        usage_regex = _re.compile(
            r'^usage: ([a-z]+) init \[-h\] client_spec\s+')
        match_obj = usage_regex.search(self._str_stream.getvalue())
        self.assertIsNotNone(match_obj)
        groups = match_obj.groups()

        self.assertEqual(groups[0], 'repobuddy')

        return

    def _test_status_help(self, args_str):
        self._hook_into_logger()
        arg_parser = ArgParser(self._handlers)
        with self.assertRaisesRegexp(ArgParserError, None) as err:
            arg_parser.parse(_shlex.split(args_str))
        self.assertTrue(err.exception.exit_prog_without_error)

        usage_regex = _re.compile(
            r'^usage: ([a-z]+) status \[-h\]\s+')
        match_obj = usage_regex.search(self._str_stream.getvalue())
        self.assertIsNotNone(match_obj)
        groups = match_obj.groups()

        self.assertEqual(groups[0], 'repobuddy')
        return

    def _test_help_unsupported_command(self, args_str):
        arg_parser = ArgParser(self._handlers)
        args = _shlex.split(args_str)
        with self.assertRaisesRegexp(
                ArgParserError,
                r'^Error: Unknown command \'' + args[-1] +
                r'\'\s+usage:') as err:
            arg_parser.parse(args)
        self.assertFalse(err.exception.exit_prog_without_error)
        return

    def _test_unsupported_command(self, args_str):
        arg_parser = ArgParser(self._handlers)
        args = _shlex.split(args_str)

        with self.assertRaises(ArgParserError) as err:
            arg_parser.parse(args)
        self.assertFalse(err.exception.exit_prog_without_error)

        error_regex = _re.compile(
            r'^([a-z]+): Error: argument command: invalid choice: \'' +
            args[0] + r'\' \(choose from (.*)\)\s+usage:')
        match_obj = error_regex.search(str(err.exception))
        self.assertIsNotNone(match_obj)
        groups = match_obj.groups()

        self.assertEqual(groups[0], 'repobuddy')
        self._assert_count_equal(
            [cmd_str.strip('\'') for cmd_str in groups[1].split(', ')],
            ['init', 'status', 'help'])
        return

    def _init_handler(self, args):
        self._last_handler = args.command
        self._last_handler_args['client_spec'] = args.client_spec
        return

    def _status_handler(self, args):
        self._last_handler = args.command
        return

    def _test_handlers(self,
                       args_str,
                       command_handler,
                       handler_name,
                       expected_handler_args):
        self._reset_handlers()
        self._handlers[handler_name] = command_handler

        ArgParser(self._handlers).parse(_shlex.split(args_str))
        self.assertEqual(self._last_handler, handler_name)
        self.assertEqual(self._last_handler_args, expected_handler_args)
        return

    def __init__(self, methodName='runTest'):
        super(ArgParserTestCase, self).__init__(methodName)
        self._original_logger_state = {'msg_stream': Logger.msg_stream,
                                       'error_stream': Logger.error_stream}
        self._handlers = {}
        self._str_stream = TestCommon.get_string_stream()
        self._last_handler = None
        self._last_handler_args = {}
        return

    def setUp(self):
        self._reset_handlers()
        return

    def test_help(self):
        self._test_help('-h')
        self._test_help('--help')
        return

    def test_version(self):
        self._test_version('-v')
        self._test_version('--version')
        return

    def test_init_help(self):
        self._test_init_help('init -h')
        self._test_init_help('init --help')
        self._test_init_help('help init')
        return

    def test_status_help(self):
        self._test_status_help('status -h')
        self._test_status_help('status --help')
        self._test_status_help('help status')
        return

    def test_help_unsupported_command(self):
        self._test_help_unsupported_command('help some-unsupported-command')
        self._test_help_unsupported_command('help invalid-command')
        return

    def test_unsupported_command(self):
        self._test_unsupported_command('some-invalid-command')
        self._test_unsupported_command('foo')
        self._test_unsupported_command('bar baz')
        return

    def test_handlers(self):
        self._test_handlers('init some-client-spec',
                            self._init_handler,
                            'init',
                            {'client_spec': 'some-client-spec'})
        self._test_handlers('status',
                            self._status_handler,
                            'status',
                            {})
        return


class ArgParserTestSuite:  # pylint: disable=W0232
    @classmethod
    def get_test_suite(cls):
        tests = [
            'test_help',
            'test_version',
            'test_init_help',
            'test_status_help',
            'test_help_unsupported_command',
            'test_unsupported_command',
            'test_handlers']
        return _unittest.TestSuite(map(ArgParserTestCase, tests))
