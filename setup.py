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

import os as _os

from setuptools import setup, find_packages

# Get the version number
execfile(_os.path.join('repobuddy', 'version.py'))

setup(
    name='RepoBuddy',
    version=__version__,    # pylint: disable=E0602
    author='Ash',
    author_email='tuxdude.github@gmail.com',
    description='Multi-repository manager for GIT based projects',
    license='Apache License 2.0',
    keywords='git repo multi-repo',
    url='https://github.com/Tuxdude/repobuddy',
    packages=find_packages(),
    package_data={
        # Include all the test manifest xml files
        'repobuddy.tests.manifests': ['*.xml'],
        # Include all the test client config files
        'repobuddy.tests.configs': ['*.config']},
    entry_points={
        'console_scripts': [
            'repobuddy = repobuddy.main:run_repobuddy',
            'test_repobuddy = repobuddy.tests.main:run_tests']}
)
