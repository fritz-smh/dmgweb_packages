# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string
from dmgweb_packages.application import app, github
from dmgweb_packages.common.package import PACKAGES_LIST, SubmissionList
import json
import os
import traceback

@app.route('/submission_list')
def submission_list():
    try:
        sub_list = SubmissionList() 
    except SubmissionError as e:
        flash(e.value, "error")
    return render_template('submission_list.html', sub_list = sub_list.list())

