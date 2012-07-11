#! /bin/bash

set -e

cwd=`pwd`
ORIGIN_REPO_URL="$cwd/testing-repo-origin"
CLONE1_REPO="$cwd/testing-repo-clone1"
CLONE2_REPO="$cwd/testing-repo-clone2"

# Clean up the directories
rm -rf $ORIGIN_REPO_URL $CLONE1_REPO $CLONE2_REPO

# Create a bare repo for remote
mkdir $ORIGIN_REPO_URL
cd $ORIGIN_REPO_URL
git init --bare

# Clone from the remote
mkdir $CLONE1_REPO
cd $CLONE1_REPO
git clone $ORIGIN_REPO_URL $CLONE1_REPO

# Create the first file
echo "This is the first commit..." > README
git add README
git commit -m "First commit."
# Create another file
echo "Another file..." > DummyFile
git add DummyFile
git commit -m "Second commit."
# Append a line to the first file
echo "Second line..." >> README
git add README
git commit -m "Adding second line."
# Push the changes to remote
git push origin master
echo "some dummy change..." >> DummyFile
# Make a change and commit, but do not push yet
git add DummyFile
git commit -m "More dummy."

# Create the second clone
cd $cwd
git clone $ORIGIN_REPO_URL $CLONE2_REPO
cd $CLONE2_REPO
# Add a new file
echo "Something" >> SOMETHING
git add SOMETHING
git commit -m "Added SOMETHING."
# Create a new branch
git branch the-other-branch
git checkout the-other-branch
# Add some more to the new file
echo "Something2" >> SOMETHING
git add SOMETHING
git commit -m "More SOMETHING."
# Add 
echo "Another line coming here..." >> README
git add README
git commit -m "Adding another line to the README."
# Push the changes in all the branches
git push origin --all

# Go back to clone1
cd $CLONE1_REPO
# Get the changes from remote and merge
git fetch origin
git pull origin master
# Now push the changes which were committed earlier
git push origin master

# Go to clone2
cd $CLONE2_REPO
# Get the changes from remote and merge
git fetch origin
git checkout master
git pull origin master
git push origin master
cd $cwd

