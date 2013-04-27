=========
RepoBuddy
=========

Multi-repository management tool for GIT

An easy alternative to git sub-modules, to configure and maintain multiple
Git repositories.

Features (planned)
------------------
-   Manage a project with multiple GIT repos.
-   XML based config file (can be versioned in GIT) with multiple
    possible configs, with each config representing a specific set of repos
    and the branches/tags which need to be cloned.
-   Sync up the latest config file, and update the local set of repos.
-   Switch between different configs seamlessly in the same local copy.

Inspired by Google's Android repo tool, but much simpler to configure,
customize and manage a project with multiple Git repositories.

Build Status
------------
**Branch dev ⇒** |dev-travis-status|

.. |dev-travis-status| image:: https://travis-ci.org/Tuxdude/repobuddy.png?branch=dev
    :target: `travis-build-status`_
    :alt: Build Status
.. _travis-build-status: https://travis-ci.org/Tuxdude/repobuddy

Bug Reports and Feature Requests
--------------------------------
Please file any and all bugs at https://github.com/Tuxdude/repobuddy/issues
Do go through the TODO.md to make sure the feature request is already not
part of it.

Contact Info
------------
Ash (Tuxdude) <tuxdude.github@gmail.com>

License
-------
RepoBuddy sources are released under GNU LGPL v3 license. Feel free to
redistribute and/or modify under the same or equivalent license.
