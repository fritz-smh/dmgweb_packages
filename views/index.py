# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app#, github

@app.route('/')
def index():
    if g.user:
        return render_template('index.html')
    else:
        return render_template('index.html')

