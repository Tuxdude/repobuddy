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

import re as _re
import shlex as _shlex
import sys as _sys

if _sys.version_info < (2, 7):
    import unittest2 as _unittest   # pylint: disable=F0401
else:
    import unittest as _unittest    # pylint: disable=F0401


from repobuddy.command_handler import CommandHandler, CommandHandlerError
from repobuddy.tests.common import TestCaseBase, TestCommon, TestSuiteManager
from repobuddy.utils import Logger


class CommandHandlerTestCase(TestCaseBase):
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

    def __init__(self, methodName='runTest'):
        super(CommandHandlerTestCase, self).__init__(methodName)
        self._original_logger_state = {'msg_stream': Logger.msg_stream,
                                       'error_stream': Logger.error_stream}
        self._str_stream = TestCommon.get_string_stream()
        return

    def setUp(self):
        return

    def test_verify_handlers(self):
        command_handler = CommandHandler()
        handlers = command_handler.get_handlers()
        self._assert_count_equal(handlers.keys(), ['init', 'status'])
        return

    def test_init_client_valid(self):
        return


class CommandHandlerTestSuite:  # pylint: disable=W0232
    @classmethod
    def get_test_suite(cls):
        tests = [
            'test_verify_handlers']
        return _unittest.TestSuite(map(CommandHandlerTestCase, tests))
