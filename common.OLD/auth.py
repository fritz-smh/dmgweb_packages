import json
import os
import logging
from dmgweb_packages.common.config import CONFIG_FILE

HARDCODED_CORE_TEAM_MEMBERS = ['fritz-smh']


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
       logging.error("Github oauth configuration : unable to open or read file '{0}')".format(CONFIG_FILE))
       raise Exception("Github oauth configuration : unable to open or read file '{0}')".format(CONFIG_FILE))
    pass



def is_core_team_member(github, domogik_organisation, username):
    core_team_members = github.get('orgs/{0}/members'.format(domogik_organisation))
    logging.debug("Check if user in core team : {0}".format(username))
    logging.debug("Hardcoded Core team members are : {0}".format(core_team_members))
    logging.debug("Core team members are : {0}".format(core_team_members))

    # handle hardcoded members
    if username in HARDCODED_CORE_TEAM_MEMBERS:
        return True

    # handle github members
    for a_member in core_team_members:
        if username == a_member['login']:
            return True
    return False


