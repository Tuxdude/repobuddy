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
.. module: client_info
   :platform: Unix, Windows
   :synopsis: Parses/Stores/Retrieves client specific configuration.
.. moduleauthor: Ash <tuxdude.github@gmail.com>

"""

import os as _os
import shutil as _shutil

from repobuddy.git_wrapper import GitWrapper, GitWrapperError
from repobuddy.utils import FileLock, FileLockError, Logger, \
    RepoBuddyBaseException
from repobuddy.manifest_parser import ManifestParser, ManifestParserError
from repobuddy.client_info import ClientInfo, ClientInfoError


class CommandHandlerError(RepoBuddyBaseException):

    """Exception raised by :class:`CommandHandler`."""

    def __init__(self, error_str):
        super(CommandHandlerError, self).__init__(error_str)
        return


class CommandHandler(object):

    """Provides handlers for the ``repobuddy`` commands."""

    def _get_manifest(self, manifest):
        """Retrieve the ``manifest`` into ``.repobuddy`` directory.

        If ``manifest`` is a file, it is copied into the ``.repobuddy``
        directory.

        As of now, the ``manifest`` argument needs to be a filename. Other
        protocols for fetching the manifest might be supported in the future.

        :param manifest: Manifest to retrieve.
        :type manifest: str
        :returns: None
        :raises: :exc:`CommandHandlerError` if unable to open the manifest.

        """
        # FIXME: Support various protcols for fetching the manifest XML file
        input_manifest = None
        if not _os.path.isabs(manifest):
            input_manifest = _os.path.join(self._current_dir,
                                           manifest)
        else:
            input_manifest = manifest

        # Copy the manifest xml file to .repobuddy dir
        try:
            _shutil.copyfile(input_manifest, self._manifest_file)
        except IOError as err:
            raise CommandHandlerError('Error: ' + str(err))
        return

    def _parse_manifest(self):
        """Parse the ``manifest``.

        :returns: None
        :raises: :exc:`CommandHandlerError` on parsing errors.

        """
        manifest_parser = ManifestParser()
        try:
            manifest_parser.parse(open(self._manifest_file, 'r'))
        except ManifestParserError as err:
            raise CommandHandlerError(str(err))

        self._manifest = manifest_parser.get_manifest()
        return

    def _get_client_spec(self, client_spec_name):
        """Retrieve the ``client_spec``.

        :param client_spec_name: The name of the client_spec.
        :type client_spec_name: str
        :returns: Client Spec
        :rtype: :class:`repobuddy.manifest_parser.ClientSpec`
        :raises: :exc:`CommandHandlerError`

        """
        client_spec = None
        for spec in self._manifest.client_spec_list:
            if spec.name == client_spec_name:
                client_spec = spec
                break
        if client_spec is None:
            raise CommandHandlerError(
                'Error: Unable to find the Client Spec: \'' +
                client_spec_name + '\'')
        return client_spec

    def _store_client_info(self, client_spec_name):
        """Write the client config to ``.repobuddy/client.config``.

        :param client_spec_name: Name of the client_spec.
        :type client_spec: str
        :returns: None
        :raises: :exc:`CommandHandlerError` on any failures in creating
            or storing the config.

        """
        try:
            client_info = ClientInfo()
            client_info.set_client_spec(client_spec_name)
            client_info.set_manifest('manifest.xml')
            client_info.write(self._client_info_file)
        except ClientInfoError as err:
            raise CommandHandlerError(str(err))
        return

    def _get_client_spec_name_from_config(self):
        """Retrieve the client_spec name from the client config.

        :returns: Value of client_spec in the config.
        :rtype: str
        :raises: :exc:`CommandHandlerError` on any failures.

        """
        try:
            client_info = ClientInfo(self._client_info_file)
            return client_info.get_client_spec()
        except ClientInfoError as err:
            raise CommandHandlerError(str(err))
        return

    def _is_client_initialized(self):
        """Determine if the client is initialized.

        :returns: ``True`` is the client is initialized, ``False`` otherwise.
        :rtype: Boolean

        """
        return _os.path.isfile(
            _os.path.join(self._repo_buddy_dir, 'client.config'))

    def _exec_with_lock(self, exec_method, *method_args):
        """Call ``exec_method`` while holding the ``.repobuddy/lock``.

        :param exec_method: The method to execute.
        :type exec_method: Reference to a method
        :param method_args: Arguments to the method.
        :type method_args: list
        :returns: None
        :raises: :exc:`CommandHandlerError` if failing to create the lock
            file or any errors in executing the method.

        """
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
        """Execute ``init`` command.

        This method needs to be called after acquiring the lock.

        :param args: Arguments to the init command.
        :type args: Namespace containing the arguments.
        :returns: None
        :raises: :exc:`CommandHandlerError` on any errors.

        """
        if self._is_client_initialized():
            raise CommandHandlerError('Error: Client is already initialized')

        # Download the manifest XML
        self._get_manifest(args.manifest)

        # Parse the manifest XML
        self._parse_manifest()

        # Get the Client Spec corresponding to the Command line argument
        client_spec = self._get_client_spec(args.client_spec)

        # Process each repo in the Client Spec
        for repo in client_spec.repo_list:
            git = GitWrapper(self._current_dir)
            git.clone(repo.url, repo.branch, repo.dest)

        # Create the client file, writing the following
        # The manifest file name
        # The client spec chosen
        self._store_client_info(args.client_spec)

        return

    def _exec_status(self):
        """Execute the ``status`` command.

        This method needs to be called after acquiring the lock.

        :returns: None
        :raises: :exc:`CommandHandlerError` on errors.

        """
        if not self._is_client_initialized():
            raise CommandHandlerError(
                'Error: Uninitialized client, ' +
                'please run init to initialize the client first')

        # Parse the manifest XML
        self._parse_manifest()

        # Get the client spec name from client info
        client = self._get_client_spec(
            self._get_client_spec_name_from_config())

        # Process each repo in the Client Spec
        for repo in client.repo_list:
            git = GitWrapper(
                _os.path.join(self._current_dir,
                              repo.dest))
            Logger.msg('####################################################')
            Logger.msg('Repo: ' + repo.dest)
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
        """Initializer."""
        self._manifest = None
        self._current_dir = _os.getcwd()
        self._repo_buddy_dir = _os.path.join(self._current_dir, '.repobuddy')
        self._manifest_file = _os.path.join(self._repo_buddy_dir,
                                            'manifest.xml')
        self._client_info_file = _os.path.join(
            self._repo_buddy_dir,
            'client.config')
        return

    def get_handlers(self):
        """Get the command handlers.

        :returns: Dictionary with command names as keys and the methods as
            values.
        :rtype: dict

        """
        handlers = {}
        handlers['init'] = self.init_command_handler
        handlers['status'] = self.status_command_handler
        return handlers

    def init_command_handler(self, args):
        """Handler for the ``init`` command.

        :returns: None
        :raises: :exc:`CommandHandlerError` on errors.

        """
        self._exec_with_lock(self._exec_init, args)
        return

    def status_command_handler(self, _args):
        """Handler for the ``status`` command.

        :returns: None
        :raises: :exc:`CommandHandlerError` on errors.

        """
        self._exec_with_lock(self._exec_status)
        return
