import json
import os

PWD = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = "{0}/../config.json".format(PWD)

def get_root_repository_url():
    ### load the json
    # check if the file exists
    if os.path.isfile(CONFIG_FILE):
        tmp_json = json.load(open(CONFIG_FILE))
        return tmp_json['root_repository']
    else:
        raise Exception("Categories : unable to open or read file '{0}')".format(CONFIG_FILE))
    pass

    
