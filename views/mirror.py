# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, send_from_directory
from flask import render_template, render_template_string
from dmgweb_packages.application import app
import os

@app.route('/mirror.tgz')
def mirror():
    return send_from_directory('{0}/../data/'.format(os.path.dirname(os.path.realpath(__file__))), 'mirror.tgz')
    
