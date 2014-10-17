How to release a new version of this tool
=========================================

Once developments are finished on the *development* branch :
* checkout on the *development* branch
* commit the last changes
* update the *CHANGELOG.md* file and commit
* create a tag : *git tag -a '1.1' -m 'Version 1.1'*
* push the last commits and the tag : *git push --tags*

Merge the new version in the *master* branch
* checkout on the *master* branch
* do the merge from the newly created tag : *git merge <tag id>*

Now, you can install the release on a server :)
