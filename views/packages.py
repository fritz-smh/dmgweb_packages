# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app, github
from dmgweb_packages.common.package import PACKAGES_LIST, PackagesList
import json
import os
import traceback

@app.route('/packages')
def packages():
    pkg_list = PackagesList()

    return render_template('packages.html', pkg_list = pkg_list.list())

