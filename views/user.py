# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from application import app, github

@app.route('/user')
def user():
    return render_template('user.html', user = github.get('user'))


