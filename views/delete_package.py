# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string

from flask_wtf import Form
from wtforms import TextField, HiddenField
from wtforms.validators import DataRequired

from dmgweb_packages.application import app, github, login_required, core_team_required
from dmgweb_packages.common.package import PackagesList, PackagesListError

import traceback
import logging


@app.route('/delete_package', methods=['POST'])
@login_required
@core_team_required
def delete_package():
    logging.info("Delete the package {0}_{1} in version {2}".format(request.form["type"], request.form["name"], request.form["version"]))
    try:
        pkg_list = PackagesList()
        pkg_list.delete(request.form["type"], request.form["name"], request.form["version"])
        flash("Package {0}_{1} in version {2} deleted from the packages list".format(request.form["type"], request.form["name"], request.form["version"]), "success")
    except:
        flash(traceback.format_exc())
    return redirect(url_for("packages")) 


