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

class RepoConfigParserError(Exception):
    def __init__(self, errorStr):
        self._errorStr = errorStr
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return repr(self._errorStr)


class Repo(object):
    def __init__(self):
        self.url = ''
        self.branch = ''
        self.destination = ''
        return


class ClientSpec(object):
    def __init__(self):
        self.name = ''
        self.repoList = [ ]
        return


class RepoConfig(object):
    def __init__(self):
        self.defaultClientSpec = ''
        self.clientSpecList = [ ]
        return


# config - a list of client specs
# Each client Spec - a list of repos
# Each repo - a dict with following keys { Url, Branch, Destination }

class _XmlContentHandler(_sax.ContentHandler):
    def _validateConfig(self):
        # Verify that defaultClientSpec is set
        if self._config.defaultClientSpec == '':
            raise RepoConfigParserError('Error: defaultClientSpec cannot be empty')
        # Verify that there is at least one element in the clientSpecList
        if len(self._config.clientSpecList) == 0:
            raise RepoConfigParserError('Error: There should be at least one valid Client Spec')
        # Verify defaultClientSpec is part of clientSpecList
        # Check for duplicate names
        foundDefaultClientSpec = False
        foundClientSpecs = set()
        for clientSpec in self._config.clientSpecList:
            if clientSpec.name == self._config.defaultClientSpec:
                foundDefaultClientSpec = True
            if clientSpec.name in foundClientSpecs:
                raise RepoConfigParserError(
                        'Error: Duplicate Client Spec \'' +
                        clientSpec.name + '\' found')
            foundClientSpecs.add(clientSpec.name)
        if not foundDefaultClientSpec:
            raise RepoConfigParserError(
                    'Error: Unable to find the Client Spec \'' +
                    self._config.defaultClientSpec +
                    '\' in the list of Repos')
        return

    def __init__(self):
        _sax.ContentHandler.__init__(self)
        return

    # Overriden methods of _sax.ContentHandler
    def startDocument(self):
        self._config = RepoConfig()
        return

    def endDocument(self):
        self._validateConfig()
        return

    def startElement(self, name, attrs):
        if name == 'RepoBuddyConfig':
            try:
                self._config.defaultClientSpec = \
                    _copy.deepcopy(str(attrs.getValue('defaultClientSpec')))
            except KeyError:
                raise RepoConfigParserError('Error: No defaultClientSpec found')
        elif name == 'ClientSpec':
            self._lastClientSpec = ClientSpec()
            try:
                self._lastClientSpec.name = attrs.getValue('name')
            except KeyError:
                raise RepoConfigParserError('Error: No name specified for ClientSpec')
        elif name == 'Repo':
            self._lastRepo = Repo()

        self._lastContent = ''
        return

    def endElement(self, name):
        if name == 'ClientSpec':
            # Add this clientspec to the config
            self._config.clientSpecList.append(self._lastClientSpec)
        elif name == 'Repo':
            # Add this repo to the clientspec
            self._lastClientSpec.repoList.append(self._lastRepo)
        elif name == 'Url':
            # Set the url key in the repo
            self._lastRepo.url = self._lastContent
        elif name == 'Branch':
            # Set the branch key in the repo
            self._lastRepo.branch = self._lastContent
        elif name == 'Destination':
            # Set the destination key in the repo
            self._lastRepo.destination = self._lastContent
        return

    def characters(self, content):
        self._lastContent += str(content)
        return

    def getConfig(self):
        return self._config


class RepoConfigParser(object):
    def __init__(self):
        self._xmlContentHandler = _XmlContentHandler()
        return

    def parse(self, fileName):
        repoConfigXmlFile = open(fileName)
        xmlParser = _XmlContentHandler()
        try:
            _sax.parse(repoConfigXmlFile, xmlParser)
        except _sax.SAXParseException as err:
            raise RepoConfigParserError(
                    'Unable to parse the RepoConfig Xml file: ' + str(err))
        finally:
            repoConfigXmlFile.close()
        self._config = xmlParser.getConfig()
        return

    def getConfig(self):
        return self._config
