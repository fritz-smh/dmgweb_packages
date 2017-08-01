# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app, github, login_required

@app.route('/user')
@login_required
def user():
    return render_template('user.html', user = github.get('user'))


