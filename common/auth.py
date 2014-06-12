
def is_core_team_member(github, domogik_organisation, username):
    core_team_members = github.get('orgs/{0}/members'.format(domogik_organisation))
    for a_member in core_team_members:
        if username == a_member['login']:
            return True
    return False


