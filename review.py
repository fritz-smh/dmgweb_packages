#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
review.py
This script is to be called as a background task from the web interface when a new package release is submitted.
"""

import traceback
import sys
import os
import json
import shutil
import time
import logging
from dmgweb_packages.common.config import Config
from subprocess import Popen, PIPE

# python 2 and 3
try:
    from urllib.request import Request, urlopen, urlencode  # Python 3
except:
    from urllib2 import Request, urlopen  # Python 2
    from urllib import urlencode  # Python 2


PWD = os.path.dirname(os.path.realpath(__file__))
LOG_FOLDER = "{0}/logs/".format(PWD)



class Review:

    def __init__(self, type, name, release, package_path):
        log.info(u"Start init")
        self.package_path = package_path

        self.config = Config()
        self.review_command = self.config.get_review_command()
        self.api_token = self.config.get_api_token()
        self.api_server = self.config.get_server_ip()
        if self.api_server == "0.0.0.0":
            # override a non usable value
            self.api_server = "127.0.0.1"
        self.api_port = self.config.get_server_port()

        self.type = type
        self.name = name
        self.release = release
        self.review_file = "{0}/data/reviews/{1}_{2}_{3}.html".format(PWD, self.type, self.name, self.release)
        log.info(self.review_file)
        if self.start_review():
            log.info(u"Set status to : AUTO_REVIEW_DONE")
            self.set_status("AUTO_REVIEW_DONE")
        else:
            log.info(u"Set status to : KO")
            self.set_status("KO")

        # TODO : build review file name from package type/name/release
        # TODO : build review file name from package type/name/release
        # TODO : build review file name from package type/name/release

        # TODO : logging (and also for crontab.py)
        # TODO : logging (and also for crontab.py)
        # TODO : logging (and also for crontab.py)

    def start_review(self):
        log.info(u"Start review for '{0} {1} {2}'...".format(self.type, self.name, self.release))
        try:
            cmd = u"{0} {1} html".format(self.review_command, self.package_path)
            log.info(u"Command is : {0}".format(cmd))
            p = Popen(cmd, 
                      stdout=PIPE,
                      stderr=PIPE,
                      shell = True)
            res = p.communicate()
            stdout = res[0]
            stderr = res[1]

            # TODO : add start datetime in human readable format
            # TODO : add start datetime in human readable format
            # TODO : add start datetime in human readable format

            content = ""
            if stderr != "":
                content += u"<h1>STDERR : </h1>\n{0}\n<h1>STDOUT : </h1>".format(stderr)
            content += u"{0}".format(stdout)
            log.info(u"Review finished for '{0} {1} {2}'...".format(self.type, self.name, self.release))
            self.save_review(content)

            # TODO : add end datetime in human readable format
            # TODO : add end datetime in human readable format
            # TODO : add end datetime in human readable format
            return True
        except:
            log.error(u"ERROR while executing review. Error is : {0}".format(traceback.format_exc()))
            # TODO : generate an review report with an error
            return False

    def save_review(self, data):
        log.info(u"Saving review for '{0} {1} {2}' in '{3}'...".format(self.type, self.name, self.release, self.review_file))
        try:
            fp = open(self.review_file, "w")
            fp.write(data)
            fp.close()
            log.info(u"Saving review finished for '{0} {1} {2}'...".format(self.type, self.name, self.release))
        except:
            log.error(u"ERROR while saving review. Error is : {0}".format(traceback.format_exc()))

    def set_status(self, status):
        log.info(u"Setting status for '{0} {1} {2}'...".format(self.type, self.name, self.release))
        url = None
        try:
            url = "http://{0}:{1}/set_status".format(self.api_server, self.api_port)
            data = {
                     "api_token" : self.api_token,      # this one override the login for some urls
                     "type" : self.type,  
                     "name" : self.name,  
                     "release" : self.release,  
                     "new_status" : status
                   }
            response = urlopen(url, data = urlencode(data))
            response_json = response.read()
            log.info(u"Setting status for '{0} {1} {2}' finished!".format(self.type, self.name, self.release))
            return "OK"
        except:
            log.error(u"ERROR while setting a status '{0}' to the package on url '{1}'. Error is : {2}".format(status, url, traceback.format_exc()))



if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(u"Usage : {0} <package type> <package name> <package release> <path to the package root (unzipped)>".format(sys.argv[0]))
        sys.exit(1)

    # logging
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    # logging - file handler
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    handler = logging.FileHandler("{0}/review.log".format(LOG_FOLDER), mode='a')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    log.addHandler(stdout_handler)
    log.info("=============================================================")

    log.info(u"Parameters :")
    log.info(u"- type = {0}".format(sys.argv[1]))
    log.info(u"- name = {0}".format(sys.argv[2]))
    log.info(u"- release = {0}".format(sys.argv[3]))
    log.info(u"- package_path = {0}".format(sys.argv[4]))
    R = Review(type = sys.argv[1],
               name = sys.argv[2],
               release = sys.argv[3],
               package_path = sys.argv[4])


