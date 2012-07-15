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
from version import __version__

import argparse as _argparse

from repobuddy.globals import HelpStrings
from repobuddy.utils import Logger, RepoBuddyBaseException


class ArgParserError(RepoBuddyBaseException):
    def __init__(self, error_str=None):
        super(ArgParserError, self).__init__(error_str)
        return


class ArgParserExitNoError(RepoBuddyBaseException):
    def __init__(self):
        super(ArgParserExitNoError, self).__init__('')
        return


# Class derived from argparse.ArgumentParser just to override the error method
# and display the help message on errors
class _MasterParser(_argparse.ArgumentParser):
    # Overriden from ArgumentParser
    # Uses Logger API to print the messages
    def _print_message(self, message, file_handle=None):
        if message:
            if file_handle is None:
                Logger.error('Writing to stderr - file is None')
            Logger.msg(message)
        return

    # Overriden from ArgumentParser
    # Raises ArgParserError instead of directly bailing out
    def exit(self, status=0, message=None):
        if not message is None:
            Logger.error(message)
        if status == 0:
            raise ArgParserExitNoError()
        else:
            raise ArgParserError()

    # Overriden from ArgumentParser
    # Stores the error message in ArgParserError instead of printing directly
    def error(self, message):
        err_msg = self.prog + ': Error: ' + message + '\n'
        err_msg += self.format_help()
        raise ArgParserError(err_msg)


# Class to configures all the argparse parsers
class ArgParser(object):
    def _display_help_init(self):
        Logger.msg(self._init_command_parser.format_help())
        return

    def _display_help_status(self):
        Logger.msg(self._status_command_parser.format_help())
        return

    def _help_command_handler(self, args):
        help_commands = {'init': self._display_help_init,
                         'status': self._display_help_status}
        try:
            help_commands[args.command]()
        except KeyError:
            raise ArgParserError(
                'Error: Unknown command \'' + args.command + '\'\n' +
                self._help_command_parser.format_help())
        return

    # Setup the master and the sub-parsers for each of the commands
    def _setup_parsers(self, handlers):
        # Top level parser
        self._master_parser = _MasterParser(
            description=HelpStrings.PROGRAM_DESCRIPTION,
            prog=HelpStrings.PROGRAM_NAME)
        self._master_parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=__version__)
        self._sub_parsers = self._master_parser.add_subparsers(
            dest='command',
            help=HelpStrings.MASTER_PARSER_ARG_HELP,
            title=HelpStrings.MASTER_PARSER_ARG_TITLE)

        # init command sub-parser
        self._init_command_parser = self._sub_parsers.add_parser(
            'init',
            help=HelpStrings.INIT_COMMAND_HELP)
        self._init_command_parser.add_argument(
            'client_spec',
            help=HelpStrings.INIT_CLIENT_SPEC_ARG)
        self._init_command_parser.set_defaults(func=handlers['init'])

        # help command sub-parser
        self._help_command_parser = self._sub_parsers.add_parser(
            'help',
            help=HelpStrings.HELP_COMMAND_HELP)
        self._help_command_parser.add_argument(
            'command',
            help=HelpStrings.HELP_COMMAND_ARG)
        self._help_command_parser.set_defaults(func=self._help_command_handler)

        # status command sub-parser
        self._status_command_parser = self._sub_parsers.add_parser(
            'status',
            help=HelpStrings.STATUS_COMMAND)
        self._status_command_parser.set_defaults(func=handlers['status'])
        return

    # Constructor
    def __init__(self, handlers):
        self._master_parser = None
        self._sub_parsers = None
        self._init_command_parser = None
        self._status_command_parser = None
        self._help_command_parser = None
        self._args = None
        self._setup_parsers(handlers)
        return

    # Parse
    def parse(self, args):
        self._args = self._master_parser.parse_args(args)
        self._args.func(self._args)
        return
