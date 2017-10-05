# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app

@app.route('/')
def index():
    #packages = app.packages.get_packages_releases()
    domogik_releases = app.domogik_releases
    packages = app.packages.get_packages()
    status = ['STABLE', 
              'BETA']
    status_with_labels = [('STABLE', 'Stable'), 
                          ('BETA', 'Beta')]
    return render_template('packages_list.html',
                           domogik_releases = domogik_releases,
                           status = status,
                           status_with_labels = status_with_labels,
                           stable_packages = True,
                           packages = packages)



@app.route('/submitted_packages')
def submitted_packages():
    #packages = app.packages.get_packages_releases()
    domogik_releases = app.domogik_releases
    packages = app.packages.get_packages()
    status = ['SUBMITTED', 
              'AUTO_REVIEW_DONE', 
              'MANUAL_REVIEW_OK']
    status_with_labels = [('SUBMITTED', 'Submitted'), 
                          ('AUTO_REVIEW_DONE', 'Automatic review done'),
                          ('MANUAL_REVIEW_OK', 'Manual review ok')]
    return render_template('packages_list.html',
                           domogik_releases = domogik_releases,
                           status = status,
                           status_with_labels = status_with_labels,
                           stable_packages = False,
                           packages = packages)

