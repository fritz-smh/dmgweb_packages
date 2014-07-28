import json
import os
import logging
from dmgweb_packages.common.config import CONFIG_FILE



class CategoriesError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Categories():

    def __init__(self):
        """ Load categories
        """
        ### load the json
        # check if the file exists
        if os.path.isfile(CONFIG_FILE):
            tmp_json = json.load(open(CONFIG_FILE))
            self.json = tmp_json['categories']
        else:
           raise CategoriesError("Categories : unable to open or read file '{0}')".format(CONFIG_FILE))
        pass

    def list(self):
        """ Return the list of categories
        """
        return self.json

    def list_for_wtf(self):
        """ Return the list of categories
        """
        the_list = []
        for elt in self.json:
            the_list.append((elt["id"], elt["name"]))
        return the_list
