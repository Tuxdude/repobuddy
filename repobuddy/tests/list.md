TEST-LIST
=========

Unit tests
----------

Fetching Repo Manifest
----------------------
1.  From file
2.  From GIT
3.  From HTTP
4.  From HTTPS
5.  From SSH

Parsing Repo Manifest
---------------------
1.  Repo String representation
2.  ClientSpec String representation
3.  Manifest String representation
4.  Invalid file handle
5.  A valid manifest
6.  A malformed manifest XML
7.  No client specs
8.  Empty client spec
9.  Client spec with no name
10. Client spec with empty Repo
11. Repo with no URL
12. Repo with empty URL
13. Repo with no branch
14. Repo with empty branch
15. Repo with no destination
16. Repo with empty destination
17. No default client spec
18. Nonexistent default client spec
19. Duplicate client spec

GitWrapper
----------
1.  Clone a repo - TODO: Needs proper validation
2.  Clone an invalid repo URL
3.  Clone a valid repo URL but invalid branch
4.  Clone a valid repo but into a directory with no write permissions
5.  Update index on a valid GIT repo
6.  Update index on an invalid GIT repo
7.  Get Untracked files when there are none
8.  Get Untracked files with 2 untracked files
9.  Get Unstaged files when there are none
10. Get Unstaged files with 2 unstaged files
11. Get Uncommitted staged files when there are none
12. Get Uncommitted staged files with 2 such files.
13. Get the current branch on a valid repo
14. Get the current branch on an invalid GIT repo
15. Get the current branch on a detached HEAD
16. Get the current tag on a lightweight TAG
17. Get the current tag on an annotated TAG
18. Get the current tag when there is none

Client Info
-----------
1.  Parse an invalid client info
2.  Parse a valid client info, and invoke all the getters
3.  Parse a valid client info, change a valid setting, and write back
4.  Parse a valid client info, change a valid setting, and write to a
    second file
5.  Create a new client info, and invoke all the getters
6.  Create a new client info, and write to a file, change a setting, and
    write to a second file
7.  Create a new client info, and write to a file with no modifications 

Utils
-----
1.  Create a lock file, and try to acquire the lock file in a second instance
2.  Create a lock file in one thread, and try to acquire the lock file in a
    second instance, while the first instance releases the lock.
3.  Create a lock file, and check if the file is created. Release the lock and
    check if the file is removed.
4.  Create a lock file in one thread, try to delete the file in another thread.
5.  Create a lock file in a directory with no write permission.

Arg Parser
----------
1.  Invoke -h and --help
2.  Invoke init -h, init --help and help init
3.  Invoke status -h, status --help and help status
4.  Invoke help -h, help --help and help help
5.  Invoke -v and --version

Command Handlers
----------------

init command
------------
1.  Initialize a client with a valid Spec
2.  Initialize a client with an invalid Spec
3.  Re-initialize a client
4.  Initialize a client from an invalid repo manifest

status command
--------------
1.  Uninitialized client
2.  No changes in any of the repos
3.  No changes, but on a different branch in one of the repo
4.  No changes, but on different branches in 2 repos
5.  3 repos - 1 with untracked change, 1 with tracked but uncommitted and
    third with staged change
6.  Committed changes and ahead of origin, but in same branch
7.  Committed changes and ahead of origin, but in a different branch
8.  Local copy in a different branch, and deleted the branch in the SPEC

General
-------
1.  No write permissions in the current dir
2.  2nd instance of repobuddy while the lock is taken
