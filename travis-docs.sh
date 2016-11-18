#!/bin/bash

GITHUB_USER="snorfalorpagus"
TARGET_BRANCH="master" # for docs
MODULES="sphinx matplotlib descartes"

# only build docs for Python 3.5 with speedups
if [ "${TRAVIS_PYTHON_VERSION}" != "3.5" ]; then
    exit 0
fi
if [ "${TRAVIS_SPEEDUP_OPTS}" != "--with-speedups" ]; then
    exit 0
fi

pip install ${MODULES}

cd docs
make html 

# Save some useful information
# TODO: change repo name
REPO="https://github.com/${GITHUB_USER}/toblerity.github.com.git"
SSH_REPO=${REPO/https:\/\/github.com\//git@github.com:}
SHA=`git rev-parse --verify HEAD`
EMAIL=`git show -s --format="%ce"`

git clone ${REPO} website
cd website
git checkout ${TARGET_BRANCH}
cd ..

# remove all of the existing files
rm -rf website/shapely/* || exit 0

# copy the new files into place
cp -R _build/html/* website/shapely/

cd website

git config --global user.name "Travis CI"
git config --global user.email "${EMAIL}"

# check for updates to the documentation
# if there are non, exit now
git diff --exit-code --quiet
if [ "$?" -eq "0" ]; then
    echo "No changes to the output on this push; exiting."
    exit 0
fi

# Commit the "changes", i.e. the new version.
# The delta will show diffs between new and old versions.
git add --all .
git commit -m "Deploy to GitHub Pages: ${SHA}"

# decrypt the ssh key
openssl aes-256-cbc -K $encrypted_c6e5bd96d87b_key -iv $encrypted_c6e5bd96d87b_iv -in ../../id_rsa.enc -out id_rsa -d

# add the key to ssh-agent
chmod 600 id_rsa
eval `ssh-agent -s`
ssh-add id_rsa

# push the update to github
git push ${SSH_REPO} ${TARGET_BRANCH}
