import json
import os
import traceback
import requests
import re
import tempfile
import magic
import zipfile
import time
import shutil
import hashlib
###from dmgweb_packages.common.tweet import tweet_message
from operator import itemgetter

# python 2 and 3
try:
    from urllib.request import urlopen
    from urllib.request import retrieve
except ImportError:
    from urllib import urlopen
    from urllib import urlretrieve





### package related configuration items

# json
JSON_FILE = "info.json"
ICON_FILE = "design/icon.png"

# dmwweb_package
ICONS_DIR = "{0}/../data/icons/".format(os.path.dirname(os.path.realpath(__file__)))
PWD = os.path.dirname(os.path.realpath(__file__))
PACKAGES = "{0}/../data/packages.json".format(PWD)

# allowed mime types for packages download
MIME_ZIP = 'application/zip'
ALLOWED_MIMES = [MIME_ZIP]

URL_REGEXP = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)



class PackageError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)



class PackageChecker():

    def __init__(self, logger, url):
        self.url = url.strip()
        self.downloaded_file = None
        self.json_data = None
        self.logger = logger
        self.logger.info(u"PackageChecker for {0}".format(url))

    def download(self):
        """ Download the package to a temporary path for analysis
        """
        # check if this is an url
        if not URL_REGEXP.search(self.url):
            self.logger.warning(u"PackageChecker : '{0}' is not a valid url".format(self.url))
            return False, "{0} is not a valid url".format(self.url)

        try:

            self.logger.info(u"PackageChecker : start downloading...")
            # create an empty temporary file
            self.downloaded_file = tempfile.NamedTemporaryFile(delete = False).name

            # process the download
            with open(self.downloaded_file, "wb") as f:
                response = requests.get(self.url, stream=False)
            
                # check the http response code
                if response.status_code != 200:
                    return False, "Error while downloading the package : HTTP {0}".format(response.status_code)

                # check the mime type
                peek = response.iter_content(256).next()
                mime = magic.from_buffer(peek, mime=True)
                if mime not in ALLOWED_MIMES:
                    return False, "The package downloaded has not a compliant mime type : {0}. The mime type should be one of these : {1}".format(mime, ALLOWED_MIMES)

                # download
                # TODO : stream mode and visuel feedback ???, see package.py in domogik for the example
                f.write(response.content)

            self.logger.info(u"PackageChecker : download finished in '{0}'".format(self.downloaded_file))

        except: 
            self.logger.warning(u"PackageChecker : download error for '{0}' : {1}".format(self.downloaded_file, traceback.format_exc()))
            return False, "Error while downloading the package : {0}".format(traceback.format_exc())
        return True, None


    def get_info_json(self):
        """ Get the info.json file from the zip
        """
        self.logger.info(u"PackageChecker : get informations for the package....")
        # get the hash of the file to check it has not change
        hash_sha256 = hashlib.sha256(open(self.downloaded_file, 'rb').read()).hexdigest()
        self.logger.info(u"PackageChecker : hash (sha256) = {0}".format(hash_sha256))
        
        # check the zip file contains what we need
        with zipfile.ZipFile(self.downloaded_file, 'r') as myzip:
            # test the zip file
            testzip = myzip.testzip()
            if testzip != None:
                self.logger.warning(u"PackageChecker : The zip seems not to be good for the file : {0}".format(testzip))
                return False, "The zip seems not to be good for the file : {0}".format(testzip)
          

            # security!!!!! check if there is no .. or / in files path
            for fic in myzip.namelist():
                if fic[0:1] == "/" or fic[0:2] == "..":
                    self.logger.warning(u"PackageChecker : Security issue ! The zip contains some files with a path starting by '/' or '..'")
                    return False, "Security issue ! The zip contains some files with a path starting by '/' or '..'"

            # we assume that the first item of the list is the master directory in the zip and so the info.json file is under it
            try:
                root_dir = myzip.namelist()[0]
            except:
                self.logger.warning(u"PackageChecker : Error while looking in the zip file : {0}".format(traceback.format_exc()))
                return False, "Error while looking in the zip file : {0}".format(traceback.format_exc())
            json_file = os.path.join(root_dir, JSON_FILE)
            try:
                fp_json = myzip.open(json_file, 'r')
            except KeyError:
                self.logger.warning(u"PackageChecker : There is no file named '{0}' in this zip archive!".format(json_file))
                return False, "There is no file named '{0}' in this zip archive!".format(json_file)
            self.json_data = json.load(fp_json)
            self.json_data["hash_sha256"] = hash_sha256

            # extract the package icon
            self.logger.info(u"PackageChecker : content of the zip file :")
            for member in myzip.namelist():
                self.logger.info(member)
            try:
                # we will copy the icon twice : 
                # - 1 for the type/name/release because the icon may change from a release to another one
                # - 1 for the type/name in case we need to display a global icon package related to no release.
                #   In this case, we assume that often the last package submitted it the last release, so the best icon
                source = myzip.open(os.path.join(root_dir, ICON_FILE))
                target = file(os.path.join(ICONS_DIR, "{0}-{1}-{2}.png".format(self.json_data['identity']['type'], self.json_data['identity']['name'], self.json_data['identity']['version'])), "wb")
                with source, target:
                    shutil.copyfileobj(source, target)

                source = myzip.open(os.path.join(root_dir, ICON_FILE))
                target2 = file(os.path.join(ICONS_DIR, "{0}-{1}.png".format(self.json_data['identity']['type'], self.json_data['identity']['name'])), "wb")
                with source, target2:
                    shutil.copyfileobj(source, target2)
            except KeyError:
                self.logger.warning(u"PackageChecker : There is no icon in this zip archive!")
                return False, "There is no icon in this zip archive!"

            self.logger.debug(u"PackageChecker : end of processing zip file")
            return True, None

        # TODO : validate json
        # how to get the PackageJson library easily ?

    def get_json(self):
        return self.json_data


    def delete_downloaded_file(self):
        """ Delete the temporary file
        """
        self.logger.info(u"PackageChecker : delete the temporary file '{0}'".format(self.downloaded_file))
        try:
            os.unlink(self.downloaded_file)
        except:
            self.logger.warning(u"PackageChecker : unable to delete {0}".format(self.downloaded_file))
            pass


    


class Packages():
    """ Class to manage the list of packages
    """

    def __init__(self, logger):
        self.logger = logger
        ### load the json
        # check if the file exists
        if os.path.isfile(PACKAGES):
            self.logger.debug(u"The packages file '{0}' exists : loading it".format(PACKAGES))
            try:
                self.json = json.load(open(PACKAGES))
            except:
                msg = u"Error while reading the packages file '{0}'. Error is : {1}".format(PACKAGES, traceback.format_exc())
                self.logger.error(msg)
                raise PackageError(msg)
        else:
            self.logger.debug(u"The packages file '{0}' does not exists : starting from an empty list".format(PACKAGES))
            self.json = []

    def list(self):
        """ Return the list of packages (not the releases, the packages)
        """
        pkg_list = []
        for pkg in self.json:
            pkg_list.append((pkg['package_id'], pkg['package_id']))
        return sorted(pkg_list)
    

    def is_package_existing(self, pkg_type, pkg_name):
        for pkg in self.json:
           if pkg["type"] == pkg_type and pkg["name"] == pkg_name:
               return True
        return False
   
    def save(self):
        """ Save the packages list
        """
        try:
            my_file = open(PACKAGES, "w")
            my_file.write(json.dumps(self.json, sort_keys=True, indent=4))
            my_file.close()
        except:
            msg = u"Unable to save the packages : {0}".format(traceback.format_exc())
            self.logger.error(msg)
            raise Exception(msg)
    

    def add(self, pkg_type, pkg_name, pkg_email, pkg_site):
        """ add a package (not a package release) to the list
        """
        self.logger.info("Add a package (not a release) : '{0}_{1}' by '{2}', website is '{3}'".format(pkg_type, pkg_name, pkg_email, pkg_site))
        pkg_data = {
                     'package_id' : '{0}-{1}'.format(pkg_type, pkg_name),
                     'type' : pkg_type,
                     'name' : pkg_name,
                     'author_email' : pkg_email,
                     'site' : pkg_site,
                     'is_new' : True,
                     'releases' : [],
                     'issues' : [],
                     'notes' : []
                   }


        # check unicity
        for pkg in self.json:
           if pkg["type"] == pkg_type and pkg["name"] == pkg_name:
               msg = "This package has already been submitted by '{0}' (unique key is type/name)".format(pkg["author_email"])
               self.logger.error(msg)
               raise PackageError(msg)
        # add in the list
        self.json.append(pkg_data)
        self.save()
        msg = "New package created : '{0}_{1}'".format(pkg_type, pkg_name)
        self.logger.info(msg)

    def add_release(self, pkg_type, pkg_name, pkg_release, pkg_url):
        """
           package format : 
              {
                'release' : '1.1',
                'url_package' : 'http://......',
                'url_documentation' : 'http://......',
                'url_tests' : 'http://......',
                'url_review' : '/reviews/plugin_weather_1.1.html',
                'status' : 'SUBMITTED',    // values : .....
                'timestamp' : 1234567890
              }
        """

        try:
            for pkg in self.json:
               if pkg["type"] == pkg_type and pkg["name"] == pkg_name:
                   # check unicity
                   for rel in pkg['releases']:
                       if pkg_release == rel['release']:
                           msg = u"This package release has already been submitted (unique key is type/name/release)"
                           self.logger.error(msg)
                           raise PackageError(msg)
    
                   # add package release to the list of releases
                   pkg_helper = PackageHelper(self.logger, pkg_type, pkg_name, pkg_url)
                   pkg_url_doc = pkg_helper.find_documentation_url()
                   pkg_url_tests = pkg_helper.find_travis_ci_status_image_url()
                   review_file = pkg_helper.get_review_file()
                   pkg_data = {
                                'release' : pkg_release,
                                'url_package' : pkg_url,
                                'url_documentation' : pkg_url_doc,
                                'url_tests' : pkg_url_tests,
                                'review' : review_file,
                                'status' : 'TO_REVIEW',
                                'timestamp' : time.time()
                              }
                   pkg['releases'].append(pkg_data)
                   self.save()
                   msg = u"New package release added : '{0}_{1}' version '{2}' from url '{3}'".format(pkg_type, pkg_name, pkg_release, pkg_url)
                   self.logger.info(msg)
        except PackageError as e:
           raise PackageError(e.value)
        except:
           msg = u"The package release could not be submitted. Error is : {0}".format(traceback.format_exc())
           self.logger.error(msg)
           raise PackageError(msg)

    def get_informations(self, pkg_type, pkg_name):
        """ Return a list of the basic informations
        """
        for pkg in self.json:
           if pkg["type"] == pkg_type and pkg["name"] == pkg_name:
               # TODO : clean releases, issues, notes
               return pkg
        return {}
            
    def get_releases(self, pkg_type, pkg_name):
        """ Return a list of the releases
        """
        for pkg in self.json:
           if pkg["type"] == pkg_type and pkg["name"] == pkg_name:
               return pkg['releases']
        return []
            
    def get_notes(self, pkg_type, pkg_name):
        """ Return a list of the notes
        """
        for pkg in self.json:
           if pkg["type"] == pkg_type and pkg["name"] == pkg_name:
               return pkg['notes']
        return []

    def get_issues(self, pkg_type, pkg_name):
        """ Return a list of the issues
        """
        pkg_helper = PackageHelper(self.logger, pkg_type, pkg_name)
        return pkg_helper.get_open_issues()

    def get_new_issue_url(self, pkg_type, pkg_name):
        """ Return a list of the issues
        """
        pkg_helper = PackageHelper(self.logger, pkg_type, pkg_name)
        return pkg_helper.get_new_issue_url()
            
    def get_pull_requests(self, pkg_type, pkg_name):
        """ Return a list of the issues
        """
        pkg_helper = PackageHelper(self.logger, pkg_type, pkg_name)
        return pkg_helper.get_open_pull_requests()

            

class PackageHelper:
    """ A helper class to automatically find usefull data from a package release url/type/name
    """

    def __init__(self, logger, pkg_type, pkg_name, pkg_url = None):
        self.github_url_prefix = "https://github.com/"

        self.logger = logger
        self.type = pkg_type
        self.name = pkg_name
        self.url = pkg_url  # url of release, not of package's website

        # TODO : dirty to do this as this is Package() that calls PackageHelper...
        self.packages = Packages(self.logger)
        self.pkg_info = self.packages.get_informations(pkg_type, pkg_name)

        # TODO : get website url and check if this is a github one

    def find_documentation_url(self):
        """
           return : url
        """
        return "http://TODO/doc"

    def find_travis_ci_status_image_url(self):
        """
           return : url of a picture
        """
        return "http://TODO/travis"

    def get_review_file(self):
        """
           return : path of review file
        """
        return "TODO.review"

    def get_new_issue_url(self):
        """ Find the new issue url
        """
        resp = None
        try:
            self.logger.debug(u"Try to find Github url to create a new issue for '{0}-{1}' from url '{2}'".format(self.type, self.name, self.pkg_info['site']))
            if not self.pkg_info['site'].startswith(self.github_url_prefix):
                self.logger.info(u"'{0}-{1}' website is not a Github one : '{2}'. The issues can't be retrieved".format(self.type, self.name, self.pkg_info['site']))
                return []
      
            user = self.pkg_info['site'].split("/")[3]
            repo = self.pkg_info['site'].split("/")[4]
            url = "https://github.com/{0}/{1}/issues/new".format(user, repo)
            resp = url

        except:
            self.logger.error(u"Error while trying to find Github new issue url for '{0}-{1}'. Error is : {2}".format(self.type, self.name, traceback.format_exc()))
        self.logger.debug(u"Github url to create new issue for '{0}-{1}' is '{2}'".format(self.type, self.name, resp))
        return resp


    def get_open_issues(self):
        """
           Call Github API v3 to get the open issues
        """
        resp = []
        try:
            self.logger.debug(u"Try to find Github issues for '{0}-{1}' from url '{2}'".format(self.type, self.name, self.pkg_info['site']))
            if not self.pkg_info['site'].startswith(self.github_url_prefix):
                self.logger.info(u"'{0}-{1}' website is not a Github one : '{2}'. The issues can't be retrieved".format(self.type, self.name, self.pkg_info['site']))
                return []
      
            user = self.pkg_info['site'].split("/")[3]
            repo = self.pkg_info['site'].split("/")[4]
            url = "https://api.github.com/repos/{0}/{1}/issues".format(user, repo)

            self.logger.debug(u"Calling Github API : '{0}'".format(url))
            issues_json = []
            try:
                response = urlopen(url)
                raw_data = response.read().decode('utf-8').strip()
                #self.logger.debug(u"Raw data : {0}".format(raw_data))
                issues_json = json.loads(raw_data)
            except:
                self.logger.warning(u"Error while calling url '{0}'. Error is : {1}".format(url, traceback.format_exc()))
                return [u"Error while calling Github API. Please check logs"]

            for issue in issues_json:
                resp.append(u"<a href='{0}'><span class='badge'>#{1} ({2})</span> {3}</a>".format(issue['html_url'], issue['number'], issue['state'], issue['title']))
                
        except:
            self.logger.error(u"Error while trying to find Github issues for '{0}-{1}'. Error is : {2}".format(self.type, self.name, traceback.format_exc()))
        return resp


    def get_open_pull_requests(self):
        """
           Call Github API v3 to get the open pull requests
        """
        resp = []
        try:
            self.logger.debug(u"Try to find Github pull requests for '{0}-{1}' from url '{2}'".format(self.type, self.name, self.pkg_info['site']))
            if not self.pkg_info['site'].startswith(self.github_url_prefix):
                self.logger.info(u"'{0}-{1}' website is not a Github one : '{2}'. The pull requests can't be retrieved".format(self.type, self.name, self.pkg_info['site']))
                return []
      
            user = self.pkg_info['site'].split("/")[3]
            repo = self.pkg_info['site'].split("/")[4]
            url = "https://api.github.com/repos/{0}/{1}/pulls".format(user, repo)

            self.logger.debug(u"Calling Github API : '{0}'".format(url))
            pulls_json = []
            try:
                response = urlopen(url)
                raw_data = response.read().decode('utf-8').strip()
                #self.logger.debug(u"Raw data : {0}".format(raw_data))
                pulls_json = json.loads(raw_data)
            except:
                self.logger.warning(u"Error while calling url '{0}'. Error is : {1}".format(url, traceback.format_exc()))
                return [u"Error while calling Github API. Please check logs"]

            for pull in pulls_json:
                resp.append(u"<a href='{0}'><span class='badge'>#{1} ({2})</span> {3}</a>".format(pull['html_url'], pull['number'], pull['state'], pull['title']))
                
        except:
            self.logger.error(u"Error while trying to find Github pull requests for '{0}-{1}'. Error is : {2}".format(self.type, self.name, traceback.format_exc()))
        return resp
