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

import sys as _sys

if _sys.version_info < (2, 7):
    import unittest2 as _unittest   # pylint: disable=F0401
else:
    import unittest as _unittest    # pylint: disable=F0401

from repobuddy.tests.common import TestCaseBase
from repobuddy.manifest_parser import ClientSpec, Manifest, Repo, \
    ManifestParser, ManifestParserError
from repobuddy.utils import ResourceHelper


class ManifestParserTestCase(TestCaseBase):
    def _parse_manifest(self, manifest_file):
        manifest_stream = ResourceHelper.open_data_file(
            'repobuddy.tests.manifests',
            manifest_file)
        manifest_parser = ManifestParser()
        manifest_parser.parse(manifest_stream)
        return manifest_parser.get_manifest()

    def __init__(self, methodName='runTest'):
        super(ManifestParserTestCase, self).__init__(methodName)
        return

    def test_repo_str_repr(self):
        repo = Repo('https://github.com/git/git.git',
                    'master',
                    'repos/git')
        expected_repo_str = '<Repo url:https://github.com/git/git.git ' + \
                            'branch:master dest:repos/git>'

        self.assertEqual(str(repo), expected_repo_str)
        self.assertEqual(repr(repo), expected_repo_str)
        return

    def test_client_spec_str_repr(self):
        client_spec = ClientSpec(
            'Spec1',
            [
                Repo('https://github.com/git/git.git',
                     'master',
                     'repos/git'),
                Repo('https://github.com/github/linguist.git',
                     'master',
                     'repos/linguist')])
        expected_client_spec_str = \
            '<ClientSpec name:Spec1 repo_list:' + \
            '[<Repo url:https://github.com/git/git.git branch:master ' + \
            'dest:repos/git>, ' + \
            '<Repo url:https://github.com/github/linguist.git ' + \
            'branch:master dest:repos/linguist>]>'

        self.assertEqual(str(client_spec), expected_client_spec_str)
        self.assertEqual(repr(client_spec), expected_client_spec_str)
        return

    def test_manifest_str_repr(self):
        manifest = Manifest(
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
                             'repos/linguist')])])
        expected_manifest_str = \
            '<Manifest default_client_spec:Spec1 client_spec_list:' + \
            '[<ClientSpec name:Spec1 repo_list:[<Repo ' + \
            'url:https://github.com/git/git.git branch:master ' + \
            'dest:repos/git>, ' + \
            '<Repo url:https://github.com/github/linguist.git ' + \
            'branch:master dest:repos/linguist>]>]>'

        self.assertEqual(str(manifest), expected_manifest_str)
        self.assertEqual(repr(manifest), expected_manifest_str)
        return

    def test_parse_invalid_file_handle(self):
        manifest_parser = ManifestParser()
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: file_handle cannot be None$'):
            manifest_parser.parse(None)

        manifest_stream = ResourceHelper.open_data_file(
            'repobuddy.tests.manifests',
            'valid.xml')
        manifest_stream.close()
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: I/O Operation on closed file_handle$'):
            manifest_parser.parse(manifest_stream)

        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: file_handle cannot be a string$'):
            manifest_parser.parse('dummy')

        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: file_handle is not a stream object$'):
            manifest_parser.parse([])
        return

    def test_valid_manifest(self):
        manifest = self._parse_manifest('valid.xml')

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

    def test_malformed(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Unable to parse the Manifest Xml file: '):
            self._parse_manifest('malformed.xml')
        return

    def test_no_client_spec(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: There should be at least one valid Client Spec$'):
            self._parse_manifest('no-clientspec.xml')
        return

    def test_empty_client_spec(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec2\' should have at least ' +
                r'one repo$'):
            self._parse_manifest('empty-clientspec.xml')
        return

    def test_client_spec_no_name(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: No name specified for ClientSpec$'):
            self._parse_manifest('clientspec-no-name.xml')
        return

    def test_empty_repo(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec1\' has no info about the Repo$'):
            self._parse_manifest('empty-repo.xml')
        return

    def test_repo_no_url(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec1\' has a Repo with no ' +
                r'\'Url\' info$'):
            self._parse_manifest('repo-no-url.xml')
        return

    def test_repo_empty_url(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec1\' has an empty Repo \'Url\'$'):
            self._parse_manifest('repo-empty-url.xml')
        return

    def test_repo_no_branch(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec1\' has a Repo with no ' +
                r'\'Branch\' info$'):
            self._parse_manifest('repo-no-branch.xml')
        return

    def test_repo_empty_branch(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec1\' has an empty Repo '
                r'\'Branch\'$'):
            self._parse_manifest('repo-empty-branch.xml')
        return

    def test_repo_no_dest(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec1\' has a Repo with no '
                r'\'Destination\' info$'):
            self._parse_manifest('repo-no-dest.xml')
        return

    def test_repo_empty_dest(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Client Spec \'Spec1\' has an empty Repo '
                r'\'Destination\'$'):
            self._parse_manifest('repo-empty-dest.xml')
        return

    def test_no_default_client_spec(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: No default_client_spec found$'):
            self._parse_manifest('no-default-clientspec.xml')
        return

    def test_empty_default_client_spec(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: default_client_spec cannot be empty$'):
            self._parse_manifest('empty-default-clientspec.xml')
        return

    def test_nonexistent_default_client_spec(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Unable to find the Client Spec \'Spec1\' in '
                r'the list of Repos$'):
            self._parse_manifest('nonexistent-default-clientspec.xml')
        return

    def test_duplicate_client_spec(self):
        with self.assertRaisesRegexp(
                ManifestParserError,
                r'^Error: Duplicate Client Spec \'Spec1\' found$'):
            self._parse_manifest('duplicate-clientspec.xml')
        return


class ManifestParserTestSuite:  # pylint: disable=W0232
    @classmethod
    def get_test_suite(cls):
        tests = [
            'test_repo_str_repr',
            'test_client_spec_str_repr',
            'test_manifest_str_repr',
            'test_parse_invalid_file_handle',
            'test_valid_manifest',
            'test_malformed',
            'test_no_client_spec',
            'test_empty_client_spec',
            'test_client_spec_no_name',
            'test_empty_repo',
            'test_repo_no_url',
            'test_repo_empty_url',
            'test_repo_no_branch',
            'test_repo_empty_branch',
            'test_repo_no_dest',
            'test_repo_empty_dest',
            'test_empty_default_client_spec',
            'test_no_default_client_spec',
            'test_nonexistent_default_client_spec',
            'test_duplicate_client_spec']
        return _unittest.TestSuite(map(ManifestParserTestCase, tests))
