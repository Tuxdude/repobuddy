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
from repobuddy.manifest_parser import ClientSpec, Manifest, Repo, \
    ManifestParser, ManifestParserError
from repobuddy.utils import ResourceHelper


class ManifestParserTestCase(TestCaseBase):
    _base_dir = None

    def _parse_manifest(self, manifest_file):
        manifest_stream = ResourceHelper.open_data_file(
            'repobuddy.tests.manifests',
            manifest_file)
        manifest_parser = ManifestParser()
        manifest_parser.parse(manifest_stream)
        return manifest_parser.get_manifest()

    @classmethod
    def set_base_dir(cls, base_dir):
        cls._base_dir = base_dir
        return

    @classmethod
    def setUpClass(cls):
        return

    @classmethod
    def tearDownClass(cls):
        return

    def __init__(self, methodName='runTest'):
        super(ManifestParserTestCase, self).__init__(methodName)
        return

    def test_valid_manifest(self):
        manifest = self._parse_manifest('manifest-valid.xml')

        expected_manifest = Manifest(
            'Spec1',
            [
                ClientSpec(
                    'Spec1',
                    [
                        Repo('https://github.com/git/git.git',
                             'master',
                             'repos/git'),
                        Repo('https://github.com/github/linguist.git',
                             'master',
                             'repos/linguist')]),
                ClientSpec(
                    'Spec2',
                    [
                        Repo('https://github.com/github/gitignore.git',
                             'master',
                             'gitignore'),
                        Repo('git://github.com/github/linguist.git',
                             'master',
                             'linguist',)]),
                ClientSpec(
                    'Spec3',
                    [
                        Repo('git://github.com/jquery/jquery.git',
                             'master',
                             'repos/jquery'),
                        Repo('git://github.com/Tuxdude/repobuddy.git',
                             'dev',
                             'repos/repobuddy'),
                        Repo('https://github.com/github/gitignore.git',
                             'master',
                             'repos/gitignore')])])

        self.assertEqual(manifest, expected_manifest)
        return

    def test_malformed_manifest(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Unable to parse the Manifest Xml file: '):
            manifest = self._parse_manifest('manifest-malformed.xml')
        return

    def test_no_client_spec(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: There should be at least one valid Client Spec$'):
            manifest = self._parse_manifest('manifest-no-clientspec.xml')
        return

    def test_empty_client_spec(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec2\' should have at least ' +
                r'one repo$'):
            manifest = self._parse_manifest('manifest-empty-clientspec.xml')
            print manifest
        return


class ManifestParserTestSuite(object):
    def __init__(self, base_test_dir):
        if not _os.path.isdir(base_test_dir):
            ShellHelper.make_dir(base_test_dir)
        ManifestParserTestCase.set_base_dir(base_test_dir)
        return

    def get_test_suite(self):
        tests = [
            'test_valid_manifest',
            'test_malformed_manifest',
            'test_no_client_spec',
            'test_empty_client_spec']
        return _unittest.TestSuite(map(ManifestParserTestCase, tests))


def setUpModule():
    return


def tearDownModule():
    return
