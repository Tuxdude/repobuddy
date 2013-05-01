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
    INIT_MANIFEST_ARG = 'The Manifest file to use for this client'
    INIT_CLIENT_SPEC_ARG = 'The Client Spec in the Manifest to use for ' + \
                           'this client'
    HELP_COMMAND_HELP = 'Show usage details for a command'
    HELP_COMMAND_ARG = 'Command to see the help message for'
    STATUS_COMMAND = 'Show status of the current client config'

    def __new__(cls):
        raise HelpStringsError('This class should not be instantiated')
