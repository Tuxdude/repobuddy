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
"""
.. module: client_info
   :platform: Unix, Windows
   :synopsis: Parses/Stores/Retrieves client specific configuration.
.. moduleauthor: Ash <tuxdude.github@gmail.com>

"""

import sys as _sys

if _sys.version_info >= (3, 0):
    import configparser as _configparser    # pylint: disable=F0401
else:
    import ConfigParser as _configparser    # pylint: disable=F0401

from repobuddy.utils import RepoBuddyBaseException


class ClientInfoError(RepoBuddyBaseException):

    """Exception raised by :class:`ClientInfo`."""

    def __init__(self, error_str):
        """Initializer.

        :param error_str: The error string to store in the exception.
        :type error_str: str

        """
        super(ClientInfoError, self).__init__(error_str)
        return


class ClientInfo(object):

    """Parses/Stores/Retrieves the client configuration."""

    def _validate_config(self):
        """Validate the config.

        Verifies that ``client_spec`` and ``manifest`` options exist in the
        ClientInfo instance.

        :returns: None

        """
        self.get_client_spec()
        self.get_manifest()
        return

    def _get_config(self, section, option):
        """Get the configuration value.

        :param section: The name of the section in the config file.
        :type section: str
        :param option: The name of the option in the config file.
        :type option: str
        :returns: The value of the option under the section.
        :raises: :exc:`ClientInfoError` when the section or the option or both
            do not exist.

        """
        try:
            return self._config.get(section, option)
        except (_configparser.NoOptionError,
                _configparser.NoSectionError) as err:
            raise ClientInfoError('Error: ' + str(err))
        return

    def _set_config(self, section, option, value):
        """Set the configuration value.

        :param section: The name of the section in the config file.
        :type section: str
        :param option: The name of the option in the config file.
        :type option: str
        :param value: The new value for the option under the section.
        :type value: str
        :returns: None
        :raises: :exc:`ClientInfoError` when the section does not exist.

        """
        try:
            self._config.set(section, option, value)
        except _configparser.NoSectionError as err:
            raise ClientInfoError('Error: ' + str(err))
        return

    def __init__(self, config_file_name=None):
        """Initializer.

        :param config_file_name: The name of the config file. If
            ``config_file_name`` is set to ``None``, the configuration is
            just stored in-memory until :meth:`write()` is invoked. Instead
            if ``config_file_name`` **is** specified, the config file is
            opened, parsed and the instance represents the state of the config
            file.
        :type config_file_name: str
        :raises: :exc:`ClientInfoError` when ``config_file_name`` is not
            ``None`` and any of the following conditions are met:

            - Failed to open the config file.
            - Parsing errors have been detected.
            - Validating the config failed.

        """
        if not config_file_name is None:
            try:
                with open(config_file_name, 'r') as file_handle:
                    self._config = _configparser.RawConfigParser()
                    try:
                        self._config.readfp(file_handle)
                    except _configparser.ParsingError as err:
                        raise ClientInfoError(
                            'Error: Parsing config failed => ' + str(err))
            except IOError as err:
                raise ClientInfoError('Error: ' + str(err))

            self._validate_config()
            self._config_file_name = config_file_name
        else:
            self._config = _configparser.RawConfigParser()
            self._config.add_section('RepoBuddyClientInfo')
            self._config_file_name = None
        return

    def set_client_spec(self, client_spec_name):
        """Set the client_spec in the config.

        :param client_spec_name: The value for ``client_spec`` in the config.
        :type client_spec_name: str
        :returns: None
        :raises: :exc:`ClientInfoError` if the config does not already have the
            ``RepoBuddyClientInfo`` section.

        """
        self._set_config('RepoBuddyClientInfo',
                         'client_spec',
                         client_spec_name)
        return

    def set_manifest(self, manifest_xml):
        """Set the ``manifest`` in the config.

        :param manifest_xml: The value for ``manifest`` in the config.
        :type manifest_xml: str
        :returns: None
        :raises: :exc:`ClientInfoError` if the config does not have the
            ``RepoBuddyClientInfo`` section.

        """
        self._set_config('RepoBuddyClientInfo', 'manifest', manifest_xml)
        return

    def get_client_spec(self):
        """Get the value of ``client_spec`` in the config.

        :returns: The value of ``client_spec`` in the config.
        :rtype: str
        :raises: :exc:`ClientInfoError` if the config does not have the
            ``client_spec`` option.

        """
        return self._get_config('RepoBuddyClientInfo', 'client_spec')

    def get_manifest(self):
        """Get the value of ``manifest`` in the config.

        :returns: The value of ``manifest`` in the config.
        :rtype: str
        :raises: :exc:`ClientInfoError` if the config does not have the
            ``manifest`` option.

        """
        return self._get_config('RepoBuddyClientInfo', 'manifest')

    def write(self, file_name=None):
        """Write the config to a file.

        If ``file_name`` is set to ``None``, the filename passed during the
        class initialization is used instead. If there was a file name
        specified during both initialization, as well as in the parameter
        ``file_name``, this method's parameter takes precedece, and the file
        name specififed during initialization remains unmodified.

        :param file_name: The name of the file to write the config into.
        :type file_name: str
        :returns: None
        :raises: :exc:`ClientInfoError` when any of the following conditions
            are met:

            - ``file_name`` parameter is ``None`` and no file name was
              provided during initialization.
            - validation of the config failed.
            - writing the config to the file failed.

        """
        # If file_name parameter is empty, check if the file name was
        # specified in the constructor
        if file_name is None:
            if self._config_file_name is None:
                raise ClientInfoError(
                    'Error: file_name parameter cannot be empty')
            else:
                file_name = self._config_file_name

        # Verify that the config is valid
        try:
            self._validate_config()
        except ClientInfoError as err:
            raise ClientInfoError(
                'Error: Missing options. ' + str(err).split('Error: ')[1])

        try:
            with open(file_name, 'w') as config_file:
                self._config.write(config_file)
        except IOError as err:
            raise ClientInfoError('Error: ' + str(err))
        return
