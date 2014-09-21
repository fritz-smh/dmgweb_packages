# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, send_from_directory
from flask import render_template, render_template_string
from dmgweb_packages.application import app#, github
import os

#@app.route('/icons/<path:filename>')
@app.route('/icons/<filename>', methods = ['GET'])
def icons(filename):
    return send_from_directory('{0}/../data/icons/'.format(os.path.dirname(os.path.realpath(__file__))), filename)
    
