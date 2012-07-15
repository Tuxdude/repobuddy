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

import os as _os
import shutil as _shutil

from repobuddy.git_wrapper import GitWrapper, GitWrapperError
from repobuddy.utils import FileLock, FileLockError, Logger, \
    RepoBuddyBaseException
from repobuddy.manifest_parser import RepoManifestParser, \
    RepoManifestParserError
from repobuddy.client_info import ClientInfo, ClientInfoError


class CommandHandlerError(RepoBuddyBaseException):
    def __init__(self, error_str):
        super(CommandHandlerError, self).__init__(error_str)
        return


class CommandHandler(object):
    def _get_manifest_xml(self):
        # FIXME: Support various protcols for fetching the manifest XML file
        input_manifest = _os.path.join(self._current_dir,
                                       'manifest/repomanifest-example.xml')

        # Copy the manifest xml file to .repobuddy dir
        try:
            _shutil.copyfile(input_manifest, self._manifest_file)
        except IOError as err:
            raise CommandHandlerError('Error: ' + str(err))
        return

    def _parse_manifest_xml(self):
        # Parse the manifest file
        repo_manifest_parser = RepoManifestParser()
        try:
            repo_manifest_parser.parse(self._manifest_file)
        except RepoManifestParserError as err:
            raise CommandHandlerError(str(err))

        self._manifest_xml = repo_manifest_parser.get_manifest()
        return

    # Retrieve the client spec corresponding to the command-line argument
    def _get_client_spec(self, client_spec_name):
        client_spec = None
        for spec in self._manifest_xml.client_spec_list:
            if spec.name == client_spec_name:
                client_spec = spec
                break
        if client_spec is None:
            raise CommandHandlerError(
                'Error: Unable to find the Client Spec: \'' +
                client_spec_name + '\'')
        return client_spec

    def _store_client_info(self, client_spec_name):
        try:
            client_info = ClientInfo()
            client_info.set_client_spec(client_spec_name)
            client_info.set_manifest_xml('manifest.xml')
            client_info.write(self._client_info_file)
        except ClientInfoError as err:
            raise CommandHandlerError(str(err))
        return

    def _get_client_info(self):
        try:
            client_info = ClientInfo(self._client_info_file)
            return client_info.get_client_spec()
        except ClientInfoError as err:
            raise CommandHandlerError(str(err))
        return

    def _is_client_initialized(self):
        return _os.path.isfile(
            _os.path.join(self._repo_buddy_dir, 'client.config'))

    # Calls exec_method while holding the .repobuddy/lock
    def _exec_with_lock(self, exec_method, *method_args):
        lock_file = _os.path.join(self._repo_buddy_dir, 'lock')

        if not _os.path.isdir(self._repo_buddy_dir):
            # Create the .repobuddy directory if it does not exist already
            try:
                _os.mkdir(self._repo_buddy_dir)
            except OSError as err:
                raise CommandHandlerError('Error: ' + str(err))
        else:
            Logger.debug('Found an existing .repobuddy directory...')

        try:
            # Acquire the lock before doing anything else
            with FileLock(lock_file):
                Logger.debug('Lock \'' + lock_file + '\' acquired')
                exec_method(*method_args)
        except FileLockError as err:
            # If it is a timeout error, it could be one of the following:
            # *** another instance of repobuddy is running
            # *** repobuddy was killed earlier without releasing the lock file
            if err.isTimeOut:
                raise CommandHandlerError(
                    'Error: Lock file ' + lock_file + ' already exists\n' +
                    'Is another instance of repobuddy running ?')
            else:
                raise CommandHandlerError(str(err))
        except GitWrapperError as err:
            raise CommandHandlerError('Error: Git said => ' + str(err))

        return

    # Init command which runs after acquiring the Lock
    def _exec_init(self, args):
        if self._is_client_initialized():
            raise CommandHandlerError('Error: Client is already initialized')

        # Download the manifest XML
        self._get_manifest_xml()

        # Parse the manifest XML
        self._parse_manifest_xml()

        # Get the Client Spec corresponding to the Command line argument
        client_spec = self._get_client_spec(args.client_spec)

        # Process each repo in the Client Spec
        for repo in client_spec.repo_list:
            git = GitWrapper(self._current_dir)
            git.clone(repo.url, repo.branch, repo.destination)

        # Create the client file, writing the following
        # The manifest file name
        # The client spec chosen
        self._store_client_info(args.client_spec)

        return

    def _exec_status(self):
        if not self._is_client_initialized():
            raise CommandHandlerError(
                'Error: Uninitialized client, ' +
                'please run init to initialize the client first')

        # Parse the manifest XML
        self._parse_manifest_xml()

        # Get the client spec name from client info
        client = self._get_client_spec(self._get_client_info())

        # Process each repo in the Client Spec
        for repo in client.repo_list:
            git = GitWrapper(
                _os.path.join(self._current_dir,
                              repo.destination))
            Logger.msg('####################################################')
            Logger.msg('Repo: ' + repo.destination)
            Logger.msg('Remote URL: ' + repo.url)
            git.update_index()
            current_branch = git.get_current_branch()
            dirty = False

            if current_branch is None:
                current_branch = 'Detached HEAD'

            if current_branch != repo.branch:
                Logger.msg('Original Branch: ' + repo.branch)
                Logger.msg('Current Branch: ' + current_branch + '\n')
            else:
                Logger.msg('Branch: ' + repo.branch + '\n')

            untracked_files = git.get_untracked_files()
            if len(untracked_files) != 0:
                Logger.msg(
                    'Untracked Files: \n' + '\n'.join(untracked_files) + '\n')
                dirty = True

            unstaged_files = git.get_unstaged_files()
            if len(unstaged_files) != 0:
                Logger.msg(
                    'Unstaged Files: \n' + '\n'.join(unstaged_files) + '\n')
                dirty = True

            uncommitted_staged_files = git.get_uncommitted_staged_files()
            if len(uncommitted_staged_files) != 0:
                Logger.msg('Uncommitted Changes: \n' +
                           '\n'.join(uncommitted_staged_files) + '\n')
                dirty = True

            if not dirty:
                Logger.msg('No uncommitted changes')
        Logger.msg('####################################################')
        return

    def __init__(self):
        self._manifest_xml = None
        self._current_dir = _os.getcwd()
        self._repo_buddy_dir = _os.path.join(self._current_dir, '.repobuddy')
        self._manifest_file = _os.path.join(self._repo_buddy_dir,
                                            'manifest.xml')
        self._client_info_file = _os.path.join(
            self._repo_buddy_dir,
            'client.config')
        return

    def get_handlers(self):
        handlers = {}
        handlers['init'] = self.init_command_handler
        handlers['status'] = self.status_command_handler
        return handlers

    def init_command_handler(self, args):
        self._exec_with_lock(self._exec_init, args)
        return

    def status_command_handler(self, _args):
        self._exec_with_lock(self._exec_status)
        return
