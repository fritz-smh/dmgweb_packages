# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app, github
from dmgweb_packages.common.package import PACKAGES_LIST, PackagesList
from dmgweb_packages.common.category import Categories, CategoriesError
import json
import os
import traceback

@app.route('/packages')
def packages():
    pkg_list = PackagesList()
    categories = Categories()
    return render_template('packages_list.html', view = 'packages_list', pkg_list = pkg_list.list(), categories = categories.list())

