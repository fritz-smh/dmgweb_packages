# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, send_from_directory
from flask import render_template, render_template_string
from dmgweb_packages.application import app#, github

#@app.route('/icons/<path:filename>')
@app.route('/icons/<filename>', methods = ['GET'])
def icons(filename):
    return send_from_directory('data/icons/', filename)
    
