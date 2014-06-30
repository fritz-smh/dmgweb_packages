# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string
from dmgweb_packages.application import app, github
from dmgweb_packages.common.package import PACKAGES_LIST, RefusedList, RefusedError
import json
import os
import traceback

@app.route('/refused_list')
def refused_list():
    try:
        ref_list = RefusedList() 
    except RefusedListError as e:
        flash(e.value, "error")
    return render_template('packages_list.html', view = 'refused_list', pkg_list = ref_list.list())

