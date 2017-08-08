# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app

@app.route('/')
def index():
    packages = app.packages.get_packages_releases()
    return render_template('index.html',
                           packages = packages)

