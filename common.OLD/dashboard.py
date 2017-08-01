import json
import os
import logging
from dmgweb_packages.common.config import CONFIG_FILE



class DashboardError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Dashboard():

    def __init__(self):
        """ Load dashboard
        """
        ### load the json
        # check if the file exists
        if os.path.isfile(CONFIG_FILE):
            tmp_json = json.load(open(CONFIG_FILE))
            self.json = tmp_json['dashboard']
        else:
           raise DashboardError("Dashboard : unable to open or read file '{0}')".format(CONFIG_FILE))
        pass

    def list_components(self):
        """ Return the list of omponents
        """
        return self.json["components"]


