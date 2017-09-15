How the review works
====================

When a new package release is submitted, the review.py tool is executed in background.

The review.py is not executed directly : the start-review.sh script is called instead : this one will build the appropriate PYTHONPATH environment variable.

The review.py tool will get as parameters the package informations : type, name, release and a folder where the package content is extracted. Then, it will get from the config.json the review command and execute it with a 'html' format parameter. The output will be put in a file generated in the folder 'data/reviews/' and named as '<type>_<name>_<release>.html'

