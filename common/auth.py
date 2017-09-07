import json
import os
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
               tmp_json['github']['callback_url'], \
               tmp_json['github']['skip']
    else:
       #app.logger.error(u"Github oauth configuration : unable to open or read file '{0}')".format(CONFIG_FILE))
       raise Exception(u"Github oauth configuration : unable to open or read file '{0}')".format(CONFIG_FILE))
    pass



# TODO : grab information from config file
def is_core_team_member(log, username):
    log.debug(u"Check if user '{0}' in core team".format(username))
    log.debug(u"Hardcoded Core team members are : {0}".format(HARDCODED_CORE_TEAM_MEMBERS))

    # handle hardcoded members
    if username in HARDCODED_CORE_TEAM_MEMBERS:
        log.debug(u"This is a core team member :)")
        return True

    # TODO : read config file
    log.debug(u"This is a core team member :)")
    return False

