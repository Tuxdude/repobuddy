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
.. module: repobuddy.arg_parser
   :platform: Unix, Windows
   :synopsis: Helper classes to parse ``repobuddy`` command line arguments.
.. moduleauthor: Ash <tuxdude.github@gmail.com>

"""

import argparse as _argparse

from repobuddy.globals import HelpStrings
from repobuddy.utils import Logger, RepoBuddyBaseException
from repobuddy.version import __version__


class ArgParserError(RepoBuddyBaseException):

    """Exception raised by :class:`ArgParser`.

    :ivar exit_prog_without_error: Set to ``True`` if :class:`ArgParser`
        completed parsing the command line arguments without any errors,
        otherwise ``False``.

    """

    def __init__(self, error_str=None, exit_prog_without_error=False):
        super(ArgParserError, self).__init__(error_str)
        self.exit_prog_without_error = exit_prog_without_error
        return


class _MasterParser(_argparse.ArgumentParser):

    """A customized argument parser class.

    An Argument Parser class to override and customize few methods from
    :class:`argparse.ArgumentParser`.

    """

    def _print_message(self, message, file_handle=None):
        """Print the message using :class:`repobuddy.utils.Logger`.

        :param message: Message to print.
        :type message: str
        :param file_handle: File handle.
        :type: stream.
        :returns: None

        """
        if message:
            if file_handle is None:
                Logger.error('Writing to stderr - file is None')
            Logger.msg(message)
        return

    def exit(self, status=0, message=None):
        """Raise :exc:`ArgParserError` instead of directly exiting.

        :param status: Status to exit the program with.
        :type status: int
        :param message: Message to print before exiting.
        :type message: str
        :returns: None
        :raises: :exc:`ArgParserError` after printing the ``message`` using
            :class:`repobuddy.utils.Logger`. ``exit_prog_without_error`` in
            :exc:`ArgParserError` is set to ``True``, if ``status`` is
            ``0``, otherwise ``False``.

        """
        if not message is None:
            Logger.error(message)
        raise ArgParserError(None, status == 0)

    def error(self, message):
        """Raise :exc:`ArgParserError` with the error message.

        :param message: Error message to print.
        :type message: str
        :returns: None
        :raises: :exc:`ArgParserError` with the ``message`` as the error
            string.

        """
        err_msg = self.prog + ': Error: ' + message + '\n'
        err_msg += self.format_help()
        raise ArgParserError(err_msg)


class ArgParser(object):

    """Parses command line arguments for ``repobuddy``."""

    def _display_help_init(self):
        """Display help on the ``init`` command.

        :returns: None

        """
        Logger.msg(self._init_command_parser.format_help())
        self._master_parser.exit(status=0)
        return

    def _display_help_status(self):
        """Display help on the ``status`` command.

        :returns: None

        """
        Logger.msg(self._status_command_parser.format_help())
        self._master_parser.exit(status=0)
        return

    def _help_command_handler(self, args):
        """Handler for the ``help`` command.

        :param args: Arguments parsed by the parser.
        :type args: Namespace containing the arguments.
        :returns: None
        :raises: :exc:`ArgParserError` if ``args.command`` is an
            unknown command.

        """
        help_commands = {'init': self._display_help_init,
                         'status': self._display_help_status}
        try:
            help_commands[args.command]()
        except KeyError:
            raise ArgParserError(
                'Error: Unknown command \'' + args.command + '\'\n' +
                self._help_command_parser.format_help())
        return

    def _setup_parsers(self, handlers):
        """Configure the argument parsers.

        Sets up the top level parser and the sub-parsers to handle all the
        ``repobuddy`` commands.

        :param handlers: A dictionary with command names as keys and the
            handler functions as values.
        :type handlers: dict
        :returns: None

        """
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
            'manifest',
            help=HelpStrings.INIT_MANIFEST_ARG)
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
        self._help_command_parser.set_defaults(
            func=self._help_command_handler)

        # status command sub-parser
        self._status_command_parser = self._sub_parsers.add_parser(
            'status',
            help=HelpStrings.STATUS_COMMAND)
        self._status_command_parser.set_defaults(func=handlers['status'])
        return

    def __init__(self, handlers):
        """Initializer.

        :param handlers: A dictionary with command names as keys and the
            handler functions as values.
        :type handlers: dict
        :returns: None

        """
        self._master_parser = None
        self._sub_parsers = None
        self._init_command_parser = None
        self._status_command_parser = None
        self._help_command_parser = None
        self._args = None
        self._setup_parsers(handlers)
        return

    def parse(self, args):
        """Parse the command line arguments to ``repobuddy``.

        :param args: List of command line arguments.
        :type args: list of strings
        :returns: None
        :raises: :exc:`ArgParserError` on parsing errors.

        """
        self._args = self._master_parser.parse_args(args)
        self._args.func(self._args)
        return
