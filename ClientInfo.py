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

import ConfigParser as _ConfigParser

class ClientInfoError(Exception):
    def __init__(self, errorStr):
        self._errorStr = errorStr
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return str(self._errorStr)

class ClientInfo(object):
    def _validateConfig(self):
        # Verify clientSpec and configXml sections exist
        return

    def _getConfig(self, section, option):
        try:
            return self._config.get(section, option)
        except _ConfigParser.NoOptionError as err:
            raise ClientInfoError('Error: ' + str(err))
        return

    def _setConfig(self, section, option, value):
        try:
            self._config.set(section, option, value)
        except _ConfigParser.NoSectionError as err:
            raise ClientInfoError('Error: ' + str(err))
        return

    def __init__(self, configFileName = None):
        if not configFileName is None:
            try:
                fd = open(configFileName, 'r')
            except IOError as err:
                raise ClientInfoError('Error: ' + str(err))

            self._config = _ConfigParser.RawConfigParser()
            try:
                self._config.readfp(fd)
            except _ConfigParser.ParsingError as err:
                raise ClientInfoError('Error: Parsing config failed => ' + str(err))
            finally:
                fd.close()

            self._validateConfig()
            self._configFileName = configFileName
        else:
            self._config = _ConfigParser.RawConfigParser()
            self._config.add_section('RepoBuddyConfig')
            self._configFileName = None

        return

    def setClientSpec(self, clientSpecName):
        self._setConfig('RepoBuddyConfig', 'clientSpec', clientSpecName)
        return

    def setXmlConfig(self, xmlConfig):
        self._setConfig('RepoBuddyConfig', 'xmlConfig', xmlConfig)
        return

    def getClientSpec(self):
        return self._getConfig('RepoBuddyConfig', 'clientSpec')

    def getXmlConfig(self):
        return self._getConfig('RepoBuddyConfig', 'xmlConfig')

    def write(self, fileName = None):
        outputFileName = fileName

        # If fileName parameter is empty, check if the file name was
        # specified in the constructor
        if outputFileName is None:
            if self._configFileName is None:
                raise ClientInfoError(
                        'Error: fileName parameter cannot be empty')
            else:
                outputFileName = self._configFileName

        try:
            with open(outputFileName, 'wb') as configFile:
                self._config.write(configFile)
        except IOError as err:
            raise ClientInfoError('Error: ' + str(err))
        return
