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

import os as _os
import shlex as _shlex
import shutil as _shutil
import sys as _sys

if _sys.version_info < (2, 7):
    import unittest2 as _unittest   # pylint: disable=F0401
else:
    import unittest as _unittest    # pylint: disable=F0401


from repobuddy.client_info import ClientInfo, ClientInfoError
from repobuddy.tests.common import ShellHelper, TestCaseBase, TestSuiteManager
from repobuddy.utils import ResourceHelper


class ClientInfoTestCase(TestCaseBase):
    @classmethod
    def setUpClass(cls):
        cls._test_base_dir = TestSuiteManager.get_base_dir()
        cls._config_base_dir = _os.path.join(cls._test_base_dir,
                                             'test-configs')
        ShellHelper.remove_dir(cls._config_base_dir)
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

    def _open_config_file(self, file_name, from_resource):
        test_config_file_name = _os.path.join(type(self)._config_base_dir,
                                              file_name)
        if from_resource:
            client_config_stream = ResourceHelper.open_data_file(
                'repobuddy.tests.configs',
                file_name)
            with open(test_config_file_name, 'wb') as test_config_file:
                _shutil.copyfileobj(client_config_stream, test_config_file)

        return test_config_file_name

    def _run_tests_expect_error(self, configs, from_resource=True):
        for file_name, expected_error in configs:
            with self.assertRaisesRegexp(ClientInfoError, expected_error):
                ClientInfo(     # pragma: no branch
                    self._open_config_file(file_name, from_resource))

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
        client_info = ClientInfo(self._open_config_file('valid.config',
                                                        from_resource=True))
        self.assertEqual('some_valid_client_spec',
                         client_info.get_client_spec())
        self.assertEqual('some_valid_manifest',
                         client_info.get_manifest())
        return

    def test_read_valid_writeback(self):
        # Open the valid.config
        config_file_name = self._open_config_file('valid.config',
                                                  from_resource=True)
        client_info = ClientInfo(config_file_name)

        config_data = ShellHelper.read_file_as_string(
            config_file_name).rstrip()

        # Write without making any changes
        client_info.write()
        self.assertEqual(
            config_data,
            ShellHelper.read_file_as_string(config_file_name).rstrip())

        # Set a new client_spec and write the changes
        config_data = config_data.replace('some_valid_client_spec',
                                          'some_other_client_spec')
        client_info.set_client_spec('some_other_client_spec')
        client_info.write()
        self.assertEqual(
            config_data,
            ShellHelper.read_file_as_string(config_file_name).rstrip())

        # Write the client_info to a new file
        updated_config = _os.path.join(type(self)._config_base_dir,
                                       'updated-valid.config')
        client_info.write(updated_config)
        self.assertEqual(
            config_data,
            ShellHelper.read_file_as_string(updated_config).rstrip())

        # Modify the manifest, and write to the original file
        client_info.set_manifest('some_other_manifest')
        client_info.write()
        self.assertEqual(
            config_data.replace('some_valid_manifest',
                                'some_other_manifest'),
            ShellHelper.read_file_as_string(config_file_name).rstrip())
        self.assertEqual(
            config_data,
            ShellHelper.read_file_as_string(updated_config).rstrip())
        return

    def test_create_new_config(self):
        target_config = _os.path.join(type(self)._config_base_dir,
                                      'newly-written.config')
        client_info = ClientInfo()
        with self.assertRaisesRegexp(
                ClientInfoError,
                'Error: Missing options. No option \'client_spec\' ' +
                'in section: \'RepoBuddyClientInfo\''):
            client_info.write(target_config)

        client_info.set_client_spec('some_client_spec')
        with self.assertRaisesRegexp(
                ClientInfoError,
                'Error: Missing options. No option \'manifest\' ' +
                'in section: \'RepoBuddyClientInfo\''):
            client_info.write(target_config)

        client_info = ClientInfo()
        client_info.set_manifest('some_manifest')
        with self.assertRaisesRegexp(
                ClientInfoError,
                'Error: Missing options. No option \'client_spec\' ' +
                'in section: \'RepoBuddyClientInfo\''):
            client_info.write(target_config)

        client_info.set_client_spec('some_new_client_spec')
        client_info.write(target_config)
        return


class ClientInfoTestSuite:  # pylint: disable=W0232
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
            'test_read_valid_writeback',
            'test_create_new_config']
        return _unittest.TestSuite(map(ClientInfoTestCase, tests))
