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

import copy as _copy
import xml.sax as _sax


class RepoManifestParserError(Exception):
    def __init__(self, error_str):
        super(RepoManifestParserError, self).__init__(error_str)
        self._error_str = error_str
        return

    def __str__(self):
        return str(self._error_str)

    def __repr__(self):
        return str(self._error_str)


class Repo(object):
    def __init__(self):
        self.url = ''
        self.branch = ''
        self.destination = ''
        return


class ClientSpec(object):
    def __init__(self):
        self.name = ''
        self.repo_list = []
        return


class RepoManifest(object):
    def __init__(self):
        self.default_client_spec = ''
        self.client_spec_list = []
        return


# manifest - a list of client specs
# Each client Spec - a list of repos
# Each repo - a dict with following keys { Url, Branch, Destination }
class _XmlContentHandler(_sax.ContentHandler):
    def _validate_manifest(self):
        # Verify that default_client_spec is set
        if self._manifest.default_client_spec == '':
            raise RepoManifestParserError(
                'Error: default_client_spec cannot be empty')
        # Verify that there is at least one element in the client_spec_list
        if len(self._manifest.client_spec_list) == 0:
            raise RepoManifestParserError(
                'Error: There should be at least one valid Client Spec')
        # Verify default_client_spec is part of client_spec_list
        # Check for duplicate names
        found_default_client_spec = False
        found_client_specs = set()
        for client_spec in self._manifest.client_spec_list:
            if client_spec.name == self._manifest.default_client_spec:
                found_default_client_spec = True
            if client_spec.name in found_client_specs:
                raise RepoManifestParserError(
                    'Error: Duplicate Client Spec \'' +
                    client_spec.name + '\' found')
            found_client_specs.add(client_spec.name)
        if not found_default_client_spec:
            raise RepoManifestParserError(
                'Error: Unable to find the Client Spec \'' +
                self._manifest.default_client_spec +
                '\' in the list of Repos')
        return

    def __init__(self):
        self._last_repo = None
        self._manifest = None
        self._last_content = None
        self._last_client_spec = None
        _sax.ContentHandler.__init__(self)
        return

    # Overriden methods of _sax.ContentHandler
    def startDocument(self):
        self._manifest = RepoManifest()
        return

    def endDocument(self):
        self._validate_manifest()
        return

    def startElement(self, name, attrs):
        if name == 'RepoBuddyManifest':
            try:
                self._manifest.default_client_spec = \
                    _copy.deepcopy(str(attrs.getValue('default_client_spec')))
            except KeyError:
                raise RepoManifestParserError(
                    'Error: No default_client_spec found')
        elif name == 'ClientSpec':
            self._last_client_spec = ClientSpec()
            try:
                self._last_client_spec.name = attrs.getValue('name')
            except KeyError:
                raise RepoManifestParserError(
                    'Error: No name specified for ClientSpec')
        elif name == 'Repo':
            self._last_repo = Repo()

        self._last_content = ''
        return

    def endElement(self, name):
        if name == 'ClientSpec':
            # Add this clientspec to the manifest
            self._manifest.client_spec_list.append(self._last_client_spec)
        elif name == 'Repo':
            # Add this repo to the clientspec
            self._last_client_spec.repo_list.append(self._last_repo)
        elif name == 'Url':
            # Set the url key in the repo
            self._last_repo.url = self._last_content
        elif name == 'Branch':
            # Set the branch key in the repo
            self._last_repo.branch = self._last_content
        elif name == 'Destination':
            # Set the destination key in the repo
            self._last_repo.destination = self._last_content
        return

    def characters(self, content):
        self._last_content += str(content)
        return

    def get_manifest(self):
        return self._manifest


class RepoManifestParser(object):
    def __init__(self):
        self._manifest = None
        return

    def parse(self, file_name):
        repo_manifest_xml_file = open(file_name)
        xml_parser = _XmlContentHandler()
        try:
            _sax.parse(repo_manifest_xml_file, xml_parser)
        except _sax.SAXParseException as err:
            raise RepoManifestParserError(
                'Unable to parse the RepoManifest Xml file: ' + str(err))
        finally:
            repo_manifest_xml_file.close()
        self._manifest = xml_parser.get_manifest()
        return

    def get_manifest(self):
        return self._manifest
