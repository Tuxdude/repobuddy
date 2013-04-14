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

from repobuddy.version import __version__

from repobuddy.utils import RepoBuddyBaseException


class HelpStringsError(RepoBuddyBaseException):
    def __init__(self, error_str):
        super(HelpStringsError, self).__init__(error_str)
        return


class HelpStrings:  # pylint: disable=W0232
    PROGRAM_DESCRIPTION = 'Multi-repo manager for Git'
    PROGRAM_NAME = 'repobuddy'
    PROGRAM_VERSION = '%(prog)s ' + __version__
    MASTER_PARSER_ARG_HELP = 'Command to invoke'
    MASTER_PARSER_ARG_TITLE = 'Available Commands'
    INIT_COMMAND_HELP = 'Init the current directory to set up the repos'
    INIT_CLIENT_SPEC_ARG = 'The Client Spec to use for this client'
    HELP_COMMAND_HELP = 'Show usage details for a command'
    HELP_COMMAND_ARG = 'Command to see the help message for'
    STATUS_COMMAND = 'Show status of the current client config'

    def __new__(cls):
        raise HelpStringsError('This class should not be instantiated')
