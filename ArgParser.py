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

import sys
import argparse
from HelpStrings import HelpStrings
from RepoBuddyUtils import Logger

# An argparse Action class
# XXX: not currently used
class _ArgParserAction(argparse.Action):
    def __call__(self, parser, namespace, values, optionString = None):
        setattr(namespace, self.dest, values)
        return

# Class derived from argparse.ArgumentParser just to override the error method
# and display the help message on errors
class _MasterParser(argparse.ArgumentParser):
    # Overriden from ArgumentParser
    # Uses Logger API to print the messages
    def _print_message(self, message, file = None):
        if message:
            if file is None:
                Logger.Error('Writing to stderr - file is None')
            Logger.Msg(message)
        return

    # Overriden from ArgumentParser
    # Raises ArgParserError instead of directly bailing out
    def exit(self, status = 0, message = None):
        if not message is None:
            Logger.Error(message)
        if status is 0:
            raise ArgParserExitNoError()
        else:
            raise ArgParserError()

    def error(self, message):
        errMsg = self.prog + ': Error: ' + message + '\n'
        errMsg += self.format_help()
        raise ArgParserError(errMsg)

class ArgParserError(Exception):
    def __init__(self, errorStr = None):
        self._errorStr = errorStr
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return repr(self._errorStr)

class ArgParserExitNoError(Exception):
    def __init__(self):
        return

# Class to configures all the argparse parsers
class ArgParser(object):
    def _displayHelpInit(self):
        Logger.Msg(self._initCommandParser.format_help())
        return

    def _displayHelpStatus(self):
        Logger.msg(self._statusCommandParser.format_help())
        return

    def _helpCommandHandler(self, args):
        helpCommands = {
                'init'      : self._displayHelpInit,
                'status'    : self._displayHelpStatus }
        try:
            helpCommands[args.command]()
        except KeyError:
            raise ArgParserError(
                    'Error: Unknown command \'' + args.command + '\'\n' +
                    self._helpCommandParser.format_help())
        return

    # Setup the master and the sub-parsers for each of the commands
    def _setupParsers(self, handlers):
        # Top level parser
        self._masterParser = _MasterParser(
                description = HelpStrings.ProgramDescription,
                prog        = HelpStrings.ProgramName)
        self._masterParser.add_argument(
                '-v',
                '--version',
                action  ='version',
                version = HelpStrings.ProgramVersion)
        self._subParsers = self._masterParser.add_subparsers(
                dest  = 'command',
                help  = HelpStrings.MasterParserArgHelp,
                title = HelpStrings.MasterParserArgTitle)

        # init command sub-parser
        self._initCommandParser = self._subParsers.add_parser(
                'init',
                help = HelpStrings.InitCommandHelp)
        self._initCommandParser.add_argument(
                'clientSpec',
                help = HelpStrings.InitClientSpecArg)
        self._initCommandParser.set_defaults(func = handlers['init'])

        # help command sub-parser
        self._helpCommandParser = self._subParsers.add_parser(
                'help',
                help = HelpStrings.HelpCommandHelp)
        self._helpCommandParser.add_argument(
                'command',
                help = HelpStrings.HelpCommandArg)
        self._helpCommandParser.set_defaults(func = self._helpCommandHandler)

        # status command sub-parser
        self._statusCommandParser = self._subParsers.add_parser(
                'status',
                help = HelpStrings.StatusCommand)
        self._statusCommandParser.set_defaults(func = handlers['status'])
        return

    # Constructor
    def __init__(self, handlers):
        self._setupParsers(handlers)
        return

    # Parse
    def parse(self, args):
        self._args = self._masterParser.parse_args(args)
        self._args.func(self._args)
        return

