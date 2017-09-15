#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
crontab.py
This script is to be called from crontab. It will do some background tasks : 
- get daily metrics about packages on metrics.domogik.org
"""

import traceback
import sys
import os
import json
import shutil
from dmgweb_packages.common.config import Config

# python 2 and 3
try:
    from urllib.request import Request, urlopen  # Python 3
except:
    from urllib2 import Request, urlopen  # Python 2


PWD = os.path.dirname(os.path.realpath(__file__))
NO_DATA_PICTURE = "static/images/no_data.png"

class DailyMetrics:

    def __init__(self, storage):
        self.storage = storage
        self.config = Config()
        self.api_server = self.config.get_server_ip()
        if self.api_server == "0.0.0.0":
            # override a non usable value
            self.api_server = "127.0.0.1"
        self.api_port = self.config.get_server_port()
        self.metrics_url = self.config.get_metrics_url()
        self.metrics_token = self.config.get_metrics_token()

    def get_packages_list(self):
        url = None
        try:
            url = "http://{0}:{1}/api/list_packages".format(self.api_server, self.api_port)
            response = urlopen(url)
            response_json = response.read()
            return json.loads(response_json)
        except:
            print(u"get_packages_list > ERROR while calling url '{0}'. Error is : {1}".format(url, traceback.format_exc()))

    def get_weekly_package_usage(self, type, name):
        try:
            url = None
            print(u"get_weekly_package_usage > {0} {1}".format(type, name))
            target_file = os.path.join(self.storage, "weekly_package_usage_{0}_{1}.png".format(type, name))
            url = "{0}/render/dashboard-solo/db/domogik-plugin?var-plugin={1}-{2}&var-version=All&theme=light&panelId=4&width=800&height=300".format(self.metrics_url, type, name)
            self.get_picture(url, target_file)
            print(u"  ...ok")
            print(u"get_weekly_package_usage > DONE")
        except:
            print(u"get_weekly_package_usage > ERROR while calling url '{0}'. Error is : {1}".format(url, traceback.format_exc()))


    def get_current_package_releases(self, type, name):
        try:
            url = None
            print(u"get_current_package_releases > {0} {1}".format(type, name))
            target_file = os.path.join(self.storage, "current_package_releases_{0}_{1}.png".format(type, name))
            url = "{0}/render/dashboard-solo/db/domogik-plugin?var-plugin={1}-{2}&var-version=All&theme=light&panelId=6&width=300&height=300".format(self.metrics_url, type, name)
            self.get_picture(url, target_file)
            print(u"  ...ok")
            print(u"get_current_package_releases > DONE")
        except:
            print(u"get_current_package_releases > ERROR while calling url '{0}'. Error is : {1}".format(url, traceback.format_exc()))


    def get_picture(self, full_url, target_file):
        try:
            print(u"- downloading...")
            q = Request(full_url)
            q.add_header("Authorization", "Bearer {0}".format(self.metrics_token))
            response = urlopen(q)
            print(u"  ...ok")
            print(u"- saving to '{0}'...".format(target_file))
            fp_target_file = open(target_file, "w")
            fp_target_file.write(response.read())
            fp_target_file.close()
            print(u"  ...ok")
            print(u"get_weekly_packages_usage > DONE")
        except:
            print(u"get_weekly_packages_usage > ERROR while calling url '{0}'. Error is : {1}".format(url, traceback.format_exc()))
            # in case of error, put a proper 'no data' picture
            try:
                shutil.copyfileobj(os.path.join(PWD, NO_DATA_PICTURE), target_file)
            except:
                print(u"get_weekly_packages_usage > ERROR while copying 'no data' picture. Error is : {0}".format(traceback.format_exc()))


if __name__ == "__main__":
    DM = DailyMetrics(storage = "{0}/data/metrics".format(PWD))
    pkg_list = DM.get_packages_list()
    for pkg in pkg_list:
        print(pkg)
        DM.get_weekly_package_usage(pkg['type'], pkg['name'])
        DM.get_current_package_releases(pkg['type'], pkg['name'])

