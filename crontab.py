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
# python 2 and 3
try:
    from urllib.request import Request, urlopen  # Python 3
except:
    from urllib2 import Request, urlopen  # Python 2


class DailyMetrics:

    def __init__(self, url, token, storage):
        self.base_url = url
        self.token = token
        self.storage = storage

    def getWeeklyPackageUsage(self, type, name):
        try:
            url = None
            print(u"getWeeklyPackageUsage > {0} {1}".format(type, name))
            target_file = os.path.join(self.storage, "weekly_package_usage_{0}_{1}.png".format(type, name))
            url = "{0}/render/dashboard-solo/db/domogik-plugin?var-plugin={1}-{2}&var-version=All&theme=light&panelId=4&width=8000&height=500".format(self.base_url, type, name)
            q = Request(url)
            q.add_header("Authorization", "Bearer {0}".format(self.token))
            response = urlopen(q)
            fp_target_file = open(target_file, "w")
            fp_target_file.write(response.read())
            fp_target_file.close()
            print(u"getWeeklyPackageUsage > DONE")
        except:
            print(u"getWeeklyPackageUsage > ERROR while calling url '{0}'. Error is : {1}".format(url, traceback.format_exc()))


if __name__ == "__main__":
    PWD = os.path.dirname(os.path.realpath(__file__))
    DM = DailyMetrics(url = "http://metrics.domogik.org:3000", token = "eyJrIjoiWFZTUzlBa0JEbTNGbzEyWEVPTHZOVUlLQVdzUEhoY0EiLCJuIjoicGFja2FnZXMuZG9tb2dpay5vcmciLCJpZCI6MX0=", storage = "{0}/static/metrics".format(PWD))
    DM.getWeeklyPackageUsage("plugin", "weather")
