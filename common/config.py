import json
import os

PWD = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = "{0}/../config.json".format(PWD)


def get_config_item(item):
    """ Generic function
    """
    ### load the json
    # check if the file exists
    if os.path.isfile(CONFIG_FILE):
        tmp_json = json.load(open(CONFIG_FILE))
        return tmp_json[item]
    else:
        raise Exception("Configuration : unable to open or read file '{0}')".format(CONFIG_FILE))
    pass



def get_server_ip():
    return get_config_item('server_ip')

def get_server_port():
    return int(get_config_item('server_port'))

def get_root_repository_url():
    """
     ### load the json
    # check if the file exists
    if os.path.isfile(CONFIG_FILE):
        tmp_json = json.load(open(CONFIG_FILE))
        return tmp_json['root_repository']
    else:
        raise Exception("Configuration : unable to open or read file '{0}')".format(CONFIG_FILE))
    pass
    """
    return get_config_item('root_repository')

    
