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
"""
.. module: repobuddy.manifest_parser
   :platform: Unix, Windows
   :synopsis: Classes to parse the ``repobuddy`` manifest.
.. moduleauthor: Ash <tuxdude.github@gmail.com>

"""

import copy as _copy
import xml.sax as _sax

from repobuddy.utils import EqualityBase, RepoBuddyBaseException


class ManifestParserError(RepoBuddyBaseException):

    """Exception raised by :class:`ManifestParser`."""

    def __init__(self, error_str):
        super(ManifestParserError, self).__init__(error_str)
        return


class Repo(EqualityBase):

    """Represents the Repository in the manifest."""

    def __init__(self, url=None, branch=None, dest=None):
        """Initializer.

        :param url: URL of the repository.
        :type url: str
        :param branch: Name of the branch to checkout.
        :type branch: str
        :dest: Destination directory.
        :type dest: str

        """
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

    """Represents the Client Spec in the manifest."""

    def __init__(self, name=None, repo_list=None):
        """Initializer.

        :param name: Name of the client spec.
        :type name: str
        :param repo_list: List of Repositories in the manifest.
        :type: list of :class:`Repo`

        """
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

    """Represents the manifest."""

    def __init__(self, default_client_spec=None, client_spec_list=None):
        """Initializer.

        :param default_client_spec: Default client spec.
        :type default_client_spec: str
        :param client_spec_list: List of client specs.
        :type client_spec_list: list of :class:`ClientSpec`

        """
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

    """Handler for the SAX XML parser events.

    Helps in parsing and storing the information from the manifest.

    """

    def _validate_manifest(self):
        """Validate the current manifest.

        :returns: None
        :raises: :exc:`ManifestParserError` on errors.

        """
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
        """Initializer."""
        self._last_repo = None
        self._manifest = None
        self._last_content = None
        self._last_client_spec = None
        _sax.ContentHandler.__init__(self)
        return

    def startDocument(self):
        """Overriden method of :class:`xml.sax.handler.ContentHandler`."""
        self._manifest = Manifest()
        return

    def endDocument(self):
        """Overriden method of :class:`xml.sax.handler.ContentHandler`."""
        self._validate_manifest()
        return

    def startElement(self, name, attrs):
        """Overriden method of :class:`xml.sax.handler.ContentHandler`."""
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
        """Overriden method of :class:`xml.sax.handler.ContentHandler`."""
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
        """Overriden method of :class:`xml.sax.handler.ContentHandler`."""
        self._last_content += str(content)
        return

    def get_manifest(self):
        """Get the manifest.

        :returns: The parsed manifest.
        :rtype: :class:`Manifest`.

        """
        return self._manifest


class ManifestParser(object):

    """Helper class for parsing the manifest XML."""

    def __init__(self):
        """Initializer."""
        self._manifest = None
        return

    def parse(self, file_handle):
        """Parse the manifest from the stream.

        :param file_handle: The stream to parse the manifest from.
        :type file_handle: File object.
        :returns: None
        :raises: :exc:`ManifestParserError` on errors.

        """
        if file_handle is None:
            raise ManifestParserError(
                'Error: file_handle cannot be None')
        try:
            basestring = basestring     # pylint: disable=W0622
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
        """Get the manifest.

        :returns: The parsed manifest.
        :rtype: :class:`Manifest`.

        """
        return self._manifest
