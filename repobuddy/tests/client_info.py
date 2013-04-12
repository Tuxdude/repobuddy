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
import shutil as _shutil
import sys as _sys

if _sys.version_info < (2, 7):
    import unittest2 as _unittest
else:
    import unittest as _unittest


from repobuddy.client_info import ClientInfo, ClientInfoError
from repobuddy.tests.common import ShellHelper, TestCaseBase, TestSuiteManager
from repobuddy.utils import ResourceHelper


class ClientInfoTestCase(TestCaseBase):
    @classmethod
    def setUpClass(cls):
        cls._test_base_dir = TestSuiteManager.get_base_dir()
        cls._config_base_dir = _os.path.join(cls._test_base_dir,
                                             'test-configs')
        ShellHelper.make_dir(cls._config_base_dir,
                             create_parent_dirs=True,
                             only_if_not_exists=True)
        return

    @classmethod
    def tearDownClass(cls):
        ShellHelper.remove_dir(cls._config_base_dir)
        return

    def __init__(self, methodName='runTest'):
        super(ClientInfoTestCase, self).__init__(methodName)
        return

    def _open_config_file(self, file_name):
        client_config_stream = ResourceHelper.open_data_file(
            'repobuddy.tests.configs',
            file_name)
        test_config_file_name = _os.path.join(type(self)._config_base_dir,
                                              file_name)
        test_config_file = open(test_config_file_name, 'wb')
        _shutil.copyfileobj(client_config_stream, test_config_file)
        test_config_file.close()
        return test_config_file_name

    def test_read_nonexistent_file(self):
        with self.assertRaisesRegexp(
                ClientInfoError,
                r'No such file or directory: \'non-existent-file\'$'):
            ClientInfo('non-existent-file')
        return

    def test_read_without_permissions(self):
        base_dir = type(self)._test_base_dir
        ShellHelper.exec_command(
            _shlex.split('sudo touch noread-client.config'),
            base_dir)
        ShellHelper.exec_command(
            _shlex.split('sudo chown root:root noread-client.config'),
            base_dir)
        ShellHelper.exec_command(
            _shlex.split('sudo chmod 600 noread-client.config'),
            base_dir)
        self._set_tear_down_cb(ShellHelper.exec_command,
                               _shlex.split('sudo rm noread-client.config'),
                               base_dir)

        with self.assertRaisesRegexp(
                ClientInfoError,
                r'Permission denied: .*noread-client.config\'$'):
            ClientInfo(_os.path.join(base_dir, 'noread-client.config'))
        return

    def test_read_malformed_file(self):
        with self.assertRaisesRegexp(
                ClientInfoError,
            r'^Error: Parsing config failed => File contains no section ' +
            r'headers\.\nfile:.*malformed-no-section-headers.config, line: '):
            ClientInfo(
                self._open_config_file('malformed-no-section-headers.config'))
        return

    def test_read_empty_file(self):
        return

    def test_read_config_format_without_client_info(self):
        return

    def test_read_just_section(self):
        return

    def test_read_just_options(self):
        return

    def test_read_no_client_spec(self):
        return

    def test_read_no_manifest(self):
        return

    def test_read_valid(self):
        return

    def test_read_valid_writeback_changes(self):
        return


class ClientInfoTestSuite:
    @classmethod
    def get_test_suite(cls):
        tests = [
            'test_read_nonexistent_file',
            'test_read_without_permissions',
            'test_read_malformed_file',
            'test_read_empty_file',
            'test_read_config_format_without_client_info',
            'test_read_just_section',
            'test_read_just_options',
            'test_read_no_client_spec',
            'test_read_no_manifest',
            'test_read_valid',
            'test_read_valid_writeback_changes']
        return _unittest.TestSuite(map(ClientInfoTestCase, tests))
