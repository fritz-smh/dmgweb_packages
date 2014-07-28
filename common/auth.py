import json
import os
import logging
from dmgweb_packages.common.config import CONFIG_FILE



def get_github_oauth_data():
    """ Load github oauth informations
    """
    ### load the json
    # check if the file exists
    if os.path.isfile(CONFIG_FILE):
        tmp_json = json.load(open(CONFIG_FILE))
        return tmp_json['github']['client_id'], \
               tmp_json['github']['client_secret'], \
               tmp_json['github']['callback_url']
    else:
       raise Exception("Github oauth configuration : unable to open or read file '{0}')".format(CONFIG_FILE))
    pass



def is_core_team_member(github, domogik_organisation, username):
    core_team_members = github.get('orgs/{0}/members'.format(domogik_organisation))
    for a_member in core_team_members:
        if username == a_member['login']:
            return True
    return False


