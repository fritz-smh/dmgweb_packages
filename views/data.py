# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string, send_from_directory
from dmgweb_packages.application import app

@app.route('/metrics/<path:path>')
def metrics(path):
    return send_from_directory('data/metrics', path)

@app.route('/reviews/<path:path>')
def reviews(path):
    return send_from_directory('data/reviews', path)
