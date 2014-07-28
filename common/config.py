import json
import os


CONFIG_FILE = "config.json"

def get_root_repository_url():
    ### load the json
    # check if the file exists
    if os.path.isfile(CONFIG_FILE):
        tmp_json = json.load(open(CONFIG_FILE))
        return tmp_json['root_repository']
    else:
        raise error("Categories : unable to open or read file '{0}')".format(CONFIG_FILE))
    pass

    
