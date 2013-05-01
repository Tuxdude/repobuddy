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

.. |dev-travis-status| image::
   https://travis-ci.org/Tuxdude/repobuddy.png?branch=dev
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

Copyright and License
---------------------
Copyright (C) 2013 Ash (Tuxdude) <tuxdude.github@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
