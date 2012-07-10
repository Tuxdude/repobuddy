TEST-LIST
=========

Unit tests
----------

General
-------
1.  No write permissions in the current dir
2.  2nd instance of repobuddy while the lock is taken

Arg Parse
---------
1.  Help Command
2.  Version Command

Fetching Repo Manifest
----------------------
1.  From file
2.  From GIT
3.  From HTTP
4.  From HTTPS
5.  From SSH

Parsing Repo Manifest
---------------------
1.  A valid manifest
2.  A malformed manifest XML
3.  No client specs
4.  One valid client spec, and another empty client spec
5.  A clientspec with no name, but valid body
6.  A clientspec with name, but empty Repo body
7.  A clientspec with Repo containing no URL tags
8.  A clientspec with Repo containing empty URL body
9.  A clientspec with Repo containing no branch tags
10. A clientspec with Repo containing empty branch body
11. A clientspec with Repo containing no destination tags
12. A clientspec with Repo containing empty destination body

GitWrapper
----------
1.  Clone a repo
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
13. Get the current branch on an invalid GIT repo
14. Get the current branch on a valid repo
15. Get the current branch on a detached HEAD
16. Get the current branch on a signed TAG
17. Get the current branch on an unsigned TAG
18. Get the current branch on an unannotated TAG
19. Get the current branch on an annotated TAG

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

Commands
--------

init
----
1.  Initialize a client with a valid Spec
2.  Initialize a client with an invalid Spec
3.  Re-initialize a client
4.  Initialize a client from an invalid repo manifest

status
------
1.  Uninitialized client
2.  No changes in any of the repos
3.  No changes, but on a different branch in one of the repo
4.  No changes, but on different branches in all of the 2 repos
5.  Uncommitted staged change in one repo, Unstaged change in another repo
6.  Committed changes and ahead of origin, but in same branch
7.  Committed changes and ahead of origin, but in a different branch
8.  Local copy in a different branch, and deleted the branch in the SPEC
