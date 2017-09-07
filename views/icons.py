# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, send_from_directory
from flask import render_template, render_template_string
from dmgweb_packages.application import app#, github
import os

@app.route('/icon/<type>/<name>', methods = ['GET'])
def icon(type, name):
    app.logger.debug(u"Get icon for '{0}-{1}'".format(type, name))
    filename = "{0}-{1}.png".format(type, name)
    return send_from_directory('{0}/../data/icons/'.format(os.path.dirname(os.path.realpath(__file__))), filename)

@app.route('/icon/<type>/<name>/<release>', methods = ['GET'])
def icon_for_release(type, name, release):
    filename = "{0}-{1}-{2}.png".format(type, name, release)
    return send_from_directory('{0}/../data/icons/'.format(os.path.dirname(os.path.realpath(__file__))), filename)

 
