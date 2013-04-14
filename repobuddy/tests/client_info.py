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

if _sys.version_info < (2, 7):      # pragma: no cover
    import unittest2 as _unittest   # pylint: disable=F0401
else:
    import unittest as _unittest    # pylint: disable=F0401


from repobuddy.client_info import ClientInfo, ClientInfoError
from repobuddy.tests.common import ShellHelper, TestCaseBase, TestSuiteManager
from repobuddy.utils import ResourceHelper


class ClientInfoTestCase(TestCaseBase):
    @classmethod
    def setUpClass(cls):        # pylint: disable=C0103
        cls._test_base_dir = TestSuiteManager.get_base_dir()
        cls._config_base_dir = _os.path.join(cls._test_base_dir,
                                             'test-configs')
        ShellHelper.make_dir(cls._config_base_dir,
                             create_parent_dirs=True,
                             only_if_not_exists=True)
        return

    @classmethod
    def tearDownClass(cls):     # pylint: disable=C0103
        ShellHelper.remove_dir(cls._config_base_dir)
        return

    def __init__(self, methodName='runTest'):   # pylint: disable=C0103
        super(ClientInfoTestCase, self).__init__(methodName)
        return

    def _open_config_file(self, file_name, from_resource):
        test_config_file_name = _os.path.join(type(self)._config_base_dir,
                                              file_name)
        if from_resource:
            client_config_stream = ResourceHelper.open_data_file(
                'repobuddy.tests.configs',
                file_name)
            test_config_file = open(test_config_file_name, 'wb')
            _shutil.copyfileobj(client_config_stream, test_config_file)
            test_config_file.close()

        return test_config_file_name

    def _run_tests_expect_error(self, configs, from_resource=True):
        for file_name, expected_error in configs:
            with self.assertRaisesRegexp(ClientInfoError, expected_error):
                ClientInfo(self._open_config_file(file_name, from_resource))
        return

    def test_read_nonexistent_file(self):
        self._run_tests_expect_error(
            [('non-existent-file.config',
              r'No such file or directory: .*non-existent-file.config\'$')],
            from_resource=False)
        return

    def test_read_without_permissions(self):
        base_dir = type(self)._test_base_dir
        config_file_name = 'noread-client.config'
        file_full_path = self._open_config_file(config_file_name,
                                                from_resource=False)

        ShellHelper.exec_command(
            _shlex.split('sudo touch ' + file_full_path),
            base_dir)
        ShellHelper.exec_command(
            _shlex.split('sudo chown root:root ' + file_full_path),
            base_dir)
        ShellHelper.exec_command(
            _shlex.split('sudo chmod 600 ' + file_full_path),
            base_dir)
        self._set_tear_down_cb(ShellHelper.exec_command,
                               _shlex.split('sudo rm ' + file_full_path),
                               base_dir)

        self._run_tests_expect_error(
            [(config_file_name,
              r'Permission denied: .*noread-client.config\'$')],
            from_resource=False)

        return

    def test_read_malformed_file(self):
        configs = [('malformed-no-section-headers.config',
                    r'^Error: Parsing config failed => File contains no ' +
                    r'section headers\.\nfile:.*' +
                    r'malformed-no-section-headers.config, line: '),
                   ('malformed-parsing-errors.config',
                    r'^Error: Parsing config failed => (File|Source) ' +
                    r'contains parsing errors: .*' +
                    r'malformed-parsing-errors.config' +
                    r'\s+\[line  2\]: \'invalid_config invalid_value\\n\'$')]
        self._run_tests_expect_error(configs)
        return

    def test_read_empty_file(self):
        self._run_tests_expect_error(
            [('empty.config',
              r'No section: \'RepoBuddyClientInfo\'$')])
        return

    def test_read_without_section_header(self):
        self._run_tests_expect_error(
            [('no-client-info.config',
              r'No section: \'RepoBuddyClientInfo\'$')])
        return

    def test_read_just_section(self):
        self._run_tests_expect_error(
            [('missing-options.config',
              r'No option \'.*\' in section: \'RepoBuddyClientInfo\'$')])
        return

    def test_read_just_options(self):
        self._run_tests_expect_error(
            [('missing-section.config',
              r'No section: \'RepoBuddyClientInfo\'$')])
        return

    def test_read_no_client_spec(self):
        self._run_tests_expect_error(
            [('missing-client-spec.config',
              r'No option \'client_spec\' in section: ' +
              r'\'RepoBuddyClientInfo\'$')])
        return

    def test_read_no_manifest(self):
        self._run_tests_expect_error(
            [('missing-manifest.config',
              r'No option \'manifest\' in section: ' +
              r'\'RepoBuddyClientInfo\'$')])
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
            'test_read_without_section_header',
            'test_read_just_section',
            'test_read_just_options',
            'test_read_no_client_spec',
            'test_read_no_manifest',
            'test_read_valid',
            'test_read_valid_writeback_changes']
        return _unittest.TestSuite(map(ClientInfoTestCase, tests))
