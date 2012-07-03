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

# An argparse Action class
# XXX: not currently used
class _ArgParserAction(argparse.Action):
    def __call__(self, parser, namespace, values, optionString=None):
        setattr(namespace, self.dest, values)
        return

# Class derived from argparse.ArgumentParser just to override the error method
# and display the help message on errors
class _MasterParser(argparse.ArgumentParser):
    # Method overriden from argparse.ArgumentParser
    def error(self, message):
        errMsg = self.prog + ': Error: ' + message + '\n'
        errMsg += self.format_help()
        raise ArgParserError(errMsg)
        return

class ArgParserError(Exception):
    def __init__(self, errorStr):
        self._errorStr = errorStr
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return repr(self._errorStr)

# Class to configures all the argparse parsers
class ArgParser(object):
    # Setup the master and the sub-parsers for each of the commands
    def _setupParsers(self, handlers):
        # Top level parser
        self._masterParser = _MasterParser(
                description = 'Multi-repo manager for Git',
                prog        = 'repobuddy')
        self._masterParser.add_argument(
                '-v',
                '--version',
                action  ='version',
                version = '%(prog)s 0.1 alpha')
        self._subParsers = self._masterParser.add_subparsers(
                dest  = 'command',
                help  = 'Command to invoke',
                title = 'Available Commands')

        # init command sub-parser
        self._initCommandParser = self._subParsers.add_parser(
                'init',
                help = 'Init the current directory to set up the repos')
        self._initCommandParser.add_argument(
                'clientSpec',
                help = 'Choose the client spec to use')
        self._initCommandParser.set_defaults(func = handlers['init'])

        # help command sub-parser
        self._helpCommandParser = self._subParsers.add_parser(
                'help',
                help = 'Show usage details for a particular command')
        self._helpCommandParser.add_argument(
                'command',
                help = 'Command to see the help message for')
        self._helpCommandParser.set_defaults(func = handlers['help'])

        # status command sub-parser
        self._statusCommandParser = self._subParsers.add_parser(
                'status',
                help = 'Show status of the current repo config')
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


