# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string

from dmgweb_packages.application import app, github, login_required, core_team_required
from dmgweb_packages.common.package import PackageChecker, PackageError
import json
import os
import sys
import traceback
import requests
import re
import tempfile
import magic
import zipfile
import time

# python 2 and 3
try:
    from urllib.request import urlopen
    from urllib.request import retrieve
except ImportError:
    from urllib import urlopen
    from urllib import urlretrieve






@app.route('/api/list_packages', methods=['GET'])
#@login_required
# no login required as this is public data
def api_list_packages():
    """ 
    """
    app.logger.debug(u"Calling /api/list_packages")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))
    try:
        packages = app.packages.list(form = False)
        return json.dumps(packages)
    except:
        app.logger.warning(u"Error while getting the packages list. Error is : {0}".format(traceback.format_exc()))
