#! /usr/bin/env python
#
#   Copyright (C) 2012 Ash (Tuxdude)
#   tuxdude.github@gmail.com
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import argparse

# An argparse Action class
# XXX: not currently used
class ArgParserAction(argparse.Action):
    def __call__(self, parser, namespace, values, optionString=None):
        setattr(namespace, self.dest, values)

# Class derived from argparse.ArgumentParser just to override the error method
# and display the help message on errors
class MasterParser(argparse.ArgumentParser):
    # Method overriden from argparse.ArgumentParser
    def error(self, message):
        print self.prog + ': Error!!! ' + message + '\n'
        self.print_help()
        self.exit(2)

# Class to configures all the argparse parsers
class ArgParser:
    # init command post-parser
    def _PostParseInit(self, args):
        print "init command parsed"
        print args

    # help command post-parser
    def _PostParseHelp(self, args):
        print "help command parsed"
        print args

    # status command post-parser
    def _PostParseStatus(self, args):
        print "status command parsed"
        print args

    # Setup the master and the sub-parsers for each of the commands
    def _SetupParsers(self):
        # Top level parser
        self._masterParser = MasterParser(
                description = 'Multi-repo manager for Git',
                prog        = 'repodude')
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
                'repoConfig',
                help = 'Choose the repo config to use')
        self._initCommandParser.set_defaults(func = self._PostParseInit)

        # help command sub-parser
        self._helpCommandParser = self._subParsers.add_parser(
                'help',
                help = 'Show usage details for a particular command')
        self._helpCommandParser.add_argument(
                'command',
                help = 'Command to see the help message for')
        self._helpCommandParser.set_defaults(func = self._PostParseHelp)

        # status command sub-parser
        self._statusCommandParser = self._subParsers.add_parser(
                'status',
                help = 'Show status of the current repo config')
        self._statusCommandParser.set_defaults(func = self._PostParseStatus)
        return

    # Constructor
    def __init__(self):
        self._SetupParsers()
        return

    # Parse sys.argv
    def Parse(self):
        self._args = self._masterParser.parse_args()
        self._args.func(self._args)
        return


