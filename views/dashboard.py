# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app#, github
from dmgweb_packages.common.package import PACKAGES_LIST, PackagesList, SubmissionList
from dmgweb_packages.common.category import Categories, CategoriesError
from dmgweb_packages.common.dashboard import Dashboard, DashboardError
import json
import os
import traceback

@app.route('/dashboard')
def dashboard():
    pkg_list = PackagesList()
    sub_list = SubmissionList()
    dashboard = Dashboard()
    categories = Categories()
    return render_template('dashboard.html', 
                           pkg_list = pkg_list.list(), 
                           sub_list = sub_list.list(), 
                           components = dashboard.list_components(),
                           categories = categories.list())

