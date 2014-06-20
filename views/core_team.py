# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app, github, DOMOGIK_ORGANISATION, login_required

@app.route('/core_team')
@login_required
def core_team():
    return render_template('core_team.html', members = github.get('orgs/{0}/members'.format(DOMOGIK_ORGANISATION)))




