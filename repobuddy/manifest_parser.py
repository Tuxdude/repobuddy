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

from repobuddy.utils import EqualityBase, RepoBuddyBaseException


class ManifestParserError(RepoBuddyBaseException):
    def __init__(self, error_str):
        super(ManifestParserError, self).__init__(error_str)
        return


class Repo(EqualityBase):
    def __init__(self, url=None, branch=None, dest=None):
        self.url = url
        self.branch = branch
        self.dest = dest
        return

    def __str__(self):
        return ('<Repo url:%s branch:%s dest:%s>' %
                (self.url, self.branch, self.dest))

    def __repr__(self):
        return self.__str__()


class ClientSpec(EqualityBase):
    def __init__(self, name=None, repo_list=None):
        self.name = name
        if not repo_list is None:
            self.repo_list = repo_list[:]
        else:
            self.repo_list = None
        return

    def __str__(self):
        return ('<ClientSpec name:%s repo_list:%s>' %
                (self.name, str(self.repo_list)))

    def __repr__(self):
        return self.__str__()


class Manifest(EqualityBase):
    def __init__(self, default_client_spec=None, client_spec_list=None):
        self.default_client_spec = default_client_spec
        if not client_spec_list is None:
            self.client_spec_list = client_spec_list[:]
        else:
            self.client_spec_list = None
        return

    def __str__(self):
        return ('<Manifest default_client_spec:%s client_spec_list:%s>' %
                (self.default_client_spec, str(self.client_spec_list)))

    def __repr__(self):
        return self.__str__()


# manifest - a list of client specs
# Each client Spec - a list of repos
# Each repo - a dict with following keys { Url, Branch, Destination }
class _XmlContentHandler(_sax.ContentHandler):
    def _validate_manifest(self):
        # Verify that default_client_spec is set
        if self._manifest.default_client_spec == '':
            raise ManifestParserError(
                'Error: default_client_spec cannot be empty')
        # Verify that there is at least one element in the client_spec_list
        if self._manifest.client_spec_list is None:
            raise ManifestParserError(
                'Error: There should be at least one valid Client Spec')
        # Verify default_client_spec is part of client_spec_list
        # Check for duplicate names
        found_default_client_spec = False
        found_client_specs = set()
        for client_spec in self._manifest.client_spec_list:
            if client_spec.name == self._manifest.default_client_spec:
                found_default_client_spec = True
            if client_spec.name in found_client_specs:
                raise ManifestParserError(
                    'Error: Duplicate Client Spec \'' +
                    client_spec.name + '\' found')
            if client_spec.repo_list is None:
                raise ManifestParserError(
                    'Error: Client Spec \'%s\' should have at least one repo' %
                    client_spec.name)
            for repo in client_spec.repo_list:
                if repo.url is None and repo.branch is None and \
                        repo.dest is None:
                    raise ManifestParserError(
                        'Error: Client Spec \'%s\' ' % client_spec.name +
                        'has no info about the Repo')

                if repo.url is None:
                    raise ManifestParserError(
                        'Error: Client Spec \'%s\' ' % client_spec.name +
                        'has a Repo with no \'Url\' info')
                elif repo.url == '':
                    raise ManifestParserError(
                        'Error: Client Spec \'%s\' ' % client_spec.name +
                        'has an empty Repo \'Url\'')

                if repo.branch is None:
                    raise ManifestParserError(
                        'Error: Client Spec \'%s\' ' % client_spec.name +
                        'has a Repo with no \'Branch\' info')
                elif repo.branch == '':
                    raise ManifestParserError(
                        'Error: Client Spec \'%s\' ' % client_spec.name +
                        'has an empty Repo \'Branch\'')

                if repo.dest is None:
                    raise ManifestParserError(
                        'Error: Client Spec \'%s\' ' % client_spec.name +
                        'has a Repo with no \'Destination\' info')
                elif repo.dest == '':
                    raise ManifestParserError(
                        'Error: Client Spec \'%s\' ' % client_spec.name +
                        'has an empty Repo \'Destination\'')

            found_client_specs.add(client_spec.name)
        if not found_default_client_spec:
            raise ManifestParserError(
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
        self._manifest = Manifest()
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
                raise ManifestParserError(
                    'Error: No default_client_spec found')
        elif name == 'ClientSpec':
            if self._manifest.client_spec_list is None:
                self._manifest.client_spec_list = []
            self._last_client_spec = ClientSpec()
            try:
                self._last_client_spec.name = attrs.getValue('name')
            except KeyError:
                raise ManifestParserError(
                    'Error: No name specified for ClientSpec')
        elif name == 'Repo':
            if self._last_client_spec.repo_list is None:
                self._last_client_spec.repo_list = []
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
            # Set the dest key in the repo
            self._last_repo.dest = self._last_content
        return

    def characters(self, content):
        self._last_content += str(content)
        return

    def get_manifest(self):
        return self._manifest


class ManifestParser(object):
    def __init__(self):
        self._manifest = None
        return

    def parse(self, file_handle):
        if file_handle is None:
            raise ManifestParserError(
                'Error: file_handle cannot be None')
        try:
            basestring = basestring
        except NameError:
            # basestring is undefined in Python 3
            basestring = (str, bytes)

        if isinstance(file_handle, basestring):
            raise ManifestParserError(
                'Error: file_handle cannot be a string')

        xml_parser = _XmlContentHandler()
        try:
            _sax.parse(file_handle, xml_parser)
        except _sax.SAXParseException as err:
            raise ManifestParserError(
                'Error: Unable to parse the Manifest Xml file: ' + str(err))
        except ValueError:
            raise ManifestParserError(
                'Error: I/O Operation on closed file_handle')
        except AttributeError:
            raise ManifestParserError(
                'Error: file_handle is not a stream object')
        finally:
            try:
                file_handle.close()
            except AttributeError:
                pass
        self._manifest = xml_parser.get_manifest()
        return

    def get_manifest(self):
        return self._manifest
