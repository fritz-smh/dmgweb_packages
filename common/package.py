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
import logging
from dmgweb_packages.common.category import Categories, CategoriesError
from dmgweb_packages.common.tweet import tweet_message
from operator import itemgetter




### package related configuration items

# json
JSON_FILE = "info.json"
ICON_FILE = "design/icon.png"
# dmwweb_package
ICONS_DIR = "{0}/../data/icons/".format(os.path.dirname(os.path.realpath(__file__)))

PWD = os.path.dirname(os.path.realpath(__file__))
PACKAGES_LIST = "{0}/../data/packages.json".format(PWD)
SUBMITTED_PACKAGES_LIST = "{0}/../data/submitted_packages.json".format(PWD)
REFUSED_PACKAGES_LIST = "{0}/../data/refused_packages.json".format(PWD)
IN_DEVELOPMENT_PACKAGES_LIST = "{0}/../data/in_development_packages.json".format(PWD)


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



class PackagesListError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SubmissionError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RefusedError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PackageChecker():

    def __init__(self, url):
        self.url = url
        self.downloaded_file = None
        self.json_data = None
        logging.info("PackageChecker for {0}".format(url))

    def download(self):
        """ Download the package to a temporary path for analysis
        """
        # check if this is an url
        if not URL_REGEXP.search(self.url):
            logging.warning("PackageChecker : '{0}' is not a valid url".format(self.url))
            return False, "{0} is not a valid url".format(self.url)

        try:

            logging.info("PackageChecker : start downloading...")
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

            logging.info("PackageChecker : download finished in '{0}'".format(self.downloaded_file))

        except: 
            logging.warning("PackageChecker : download error for '{0}' : {1}".format(self.downloaded_file, traceback.format_exc()))
            return False, "Error while downloading the package : {0}".format(traceback.format_exc())
        return True, None


    def get_info_json(self):
        """ Get the info.json file from the zip
        """
        logging.info("PackageChecker : get informations for the package....")
        # get the hash of the file to check it has not change
        hash_sha256 = hashlib.sha256(open(self.downloaded_file, 'rb').read()).hexdigest()
        logging.info("PackageChecker : hash (sha256) = {0}".format(hash_sha256))
        
        # check the zip file contains what we need
        with zipfile.ZipFile(self.downloaded_file, 'r') as myzip:
            # test the zip file
            testzip = myzip.testzip()
            if testzip != None:
                logging.warning("PackageChecker : The zip seems not to be good for the file : {0}".format(testzip))
                return False, "The zip seems not to be good for the file : {0}".format(testzip)
          

            # security!!!!! check if there is no .. or / in files path
            for fic in myzip.namelist():
                if fic[0:1] == "/" or fic[0:2] == "..":
                    logging.warning("PackageChecker : Security issue ! The zip contains some files with a path starting by '/' or '..'")
                    return False, "Security issue ! The zip contains some files with a path starting by '/' or '..'"

            # we assume that the first item of the list is the master directory in the zip and so the info.json file is under it
            try:
                root_dir = myzip.namelist()[0]
            except:
                logging.warning("PackageChecker : Error while looking in the zip file : {0}".format(traceback.format_exc()))
                return False, "Error while looking in the zip file : {0}".format(traceback.format_exc())
            json_file = os.path.join(root_dir, JSON_FILE)
            try:
                fp_json = myzip.open(json_file, 'r')
            except KeyError:
                logging.warning("PackageChecker : There is no file named '{0}' in this zip archive!".format(json_file))
                return False, "There is no file named '{0}' in this zip archive!".format(json_file)
            self.json_data = json.load(fp_json)
            self.json_data["hash_sha256"] = hash_sha256

            # extract the package icon
            logging.info("PackageChecker : content of the zip file :")
            #for member in myzip.namelist():
            #    logging.info(member)
            try:
                source = myzip.open(os.path.join(root_dir, ICON_FILE))
                target = file(os.path.join(ICONS_DIR, "{0}_{1}_{2}.png".format(self.json_data['identity']['type'], self.json_data['identity']['name'], self.json_data['identity']['version'])), "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
            except KeyError:
                logging.warning("PackageChecker : There is no icon in this zip archive!")
                return False, "There is no icon in this zip archive!"

            return True, None

        # TODO : validate json
        # how to get the PackageJson library easily ?

    def get_json(self):
        return self.json_data


    def delete_downloaded_file(self):
        """ Delete the temporary file
        """
        logging.info("PackageChecker : delete the temporary file '{0}'".format(self.downloaded_file))
        try:
            os.unlink(self.downloaded_file)
        except:
            logging.warning("PackageChecker : unable to delete {0}".format(self.downloaded_file))
            pass



class PackagesList():
    """ Class to manage the list of validated packages
    """

    def __init__(self):
        ### load the json
        # check if the file exists
        if os.path.isfile(PACKAGES_LIST):
            self.json = json.load(open(PACKAGES_LIST))
        else:
            self.json = []
        pass

    def list(self):
        """ Return the list of the packages
        """
        data = self.json
        return sorted(data,key=itemgetter('type', 'name', 'version'))
    
    def add(self, data):
        """ add a package to the packages list
        """
        logging.info("New package : {0}_{1} in version {2}".format(data["type"], data["name"], data["version"]))
        # check unicity
        for pkg in self.json:
            if pkg["type"] == data["type"] and pkg["name"] == data["name"] and  pkg["version"] == data["version"]:
                msg = "This package has already been validated by {0} (unique key is type/name/version)".format(pkg["submitter"])
                logging.error(msg)
                raise PackagesListError(msg)
                return
        # add in the list
        self.json.append(data)
        self.save()
        msg = "New package validated: {0}_{1} in version {2}".format(data["type"], data["name"], data["version"])
        logging.info(msg)
        tweet_message(msg)

    def delete(self, type, name, version):
        """ delete a package from the submission list
        """
        logging.info("Delete package : {0}_{1} in version {2}".format(type, name, version))
        # Keep all packages excepting the one
        try:
            self.json_buf = []
            for pkg in self.json:
               if not (pkg["type"] == type and pkg["name"] == name and  pkg["version"] == version):
                   self.json_buf.append(pkg)
            # add in the list
            self.json = self.json_buf
            self.save()
            msg = "Package deleted from the packages list: {0}_{1} in version {2}".format(type, name, version)
            logging.info(msg)
            tweet_message(msg)
        except:
            msg = "Unable to remove from the packages list : {0}".format(traceback.format_exc())
            logging.error(msg)
            raise Exception(msg)

    def save(self):
        """ Save the list of packages
        """
        try:
            my_file = open(PACKAGES_LIST, "w")
            my_file.write(json.dumps(self.json, sort_keys = True))
            my_file.close()
        except:
            msg = "Unable to save the packages list : {0}".format(traceback.format_exc())
            logging.error(msg)
            raise Exception(msg)
    
    def set_category(self, type, name, version, category):
        """ change the category of a package from the submission list
        """
        the_categories = Categories().list()
        try:
            self.json_buf = []
            for pkg in self.json:
               if pkg["type"] == type and pkg["name"] == name and  pkg["version"] == version:
                   # for 'is_development' category, move in the 'in development' packages json file
                   # for regular categories, just update the json
                   # for 'submission_list' value (hardcoded in the template choices), move in the submission list
                   cat_type = 'regular'
                   if category == 'submission_list':
                       cat_type = 'submission'
                   else:
                       for a_category in the_categories:
                           if a_category['id'] == category:
                               if a_category['is_development']:
                                   cat_type = 'development'
                               break

                   if cat_type == 'regular':
                       pkg["category"] = category
                       self.save()
                       msg = "Package {0}_{1} in version {2} moved to category {3}".format(type, name, version, category)
                       logging.info(msg)
                       tweet_message(msg)
                       break
                   elif cat_type == 'development':
                       # add in the 'in development' list
                       pkg_list = DevelopmentList()
                       pkg_list.add(pkg)
                       # delete in the current list
                       self.delete(type, name, version)
                       msg = "Package {0}_{1} in version {2} moved in the 'in development' packages list".format(type, name, version)
                       logging.info(msg)
                       tweet_message(msg)
                   elif cat_type == 'submission':
                       # add in the submission list
                       pkg_list = SubmissionList()
                       pkg_list.add(pkg)
                       # delete in the current list
                       self.delete(type, name, version)
                       msg = "Package {0}_{1} in version {2} moved back in the submission list".format(type, name, version)
                       logging.info(msg)
                       tweet_message(msg)
                   else:
                       msg = "WTF, I am not able to find in which category I have to move the package!!!"
                       logging.error(msg)
                       raise Exception(msg)
                    
        except:
            msg = "Unable to change the categery for the packages list : {0}".format(traceback.format_exc())
            logging.error(msg)
            raise Exception(msg)





class SubmissionList():
    """ Class to manage the list of submitted packages
    """

    def __init__(self):
        ### load the json
        # check if the file exists
        if os.path.isfile(SUBMITTED_PACKAGES_LIST):
            self.json = json.load(open(SUBMITTED_PACKAGES_LIST))
            # change the tags from foo, bar, ... to a list
            for pkg in self.json:
                if type(pkg['tags']).__name__ != "list":
                    pkg['tags'] = pkg['tags'].split(",")
        else:
            self.json = []

    def list(self):
        """ Return the list of submitted packages
        """
        data = self.json
        return sorted(data,key=itemgetter('type', 'name', 'version'))
    
    def add(self, data):
        """ add a package to the submission list
        """
        logging.info("Add a package in the submission list : {0}_{1} in version {2}".format(data["type"], data["name"], data["version"]))
        # check unicity
        for pkg in self.json:
           if pkg["type"] == data["type"] and pkg["name"] == data["name"] and  pkg["version"] == data["version"]:
               msg = "This package has already been submitted by {0} (unique key is type/name/version)".format(pkg["submitter"])
               logging.error(msg)
               raise SubmissionError(msg)
        # add in the list
        self.json.append(data)
        self.save()
        msg = "New package in the submission list: {0}_{1} in version {2}".format(data["type"], data["name"], data["version"])
        logging.info(msg)
        tweet_message(msg)

    def delete(self, type, name, version):
        """ delete a package from the submission list
        """
        logging.info("Delete a package from the submission list : {0}_{1} in version {2}".format(type, name, version))
        # Keep all packages excepting the one
        try:
            self.json_buf = []
            for pkg in self.json:
               if not (pkg["type"] == type and pkg["name"] == name and  pkg["version"] == version):
                   self.json_buf.append(pkg)
            # add in the list
            self.json = self.json_buf
            self.save()
        except:
            msg = "Unable to remove from the submission list : {0}".format(traceback.format_exc())
            logging.error(msg)
            raise Exception(msg)

    def get_package(self, type, name, version):
        """ return a given package from the submission list
        """
        for pkg in self.json:
           if pkg["type"] == type and pkg["name"] == name and  pkg["version"] == version:
               return pkg
        return None

    def save(self):
        """ Save the list of submitted packages
        """
        try:
            my_file = open(SUBMITTED_PACKAGES_LIST, "w")
            my_file.write(json.dumps(self.json, sort_keys = True))
            my_file.close()
        except:
            msg = "Unable to save the submission list : {0}".format(traceback.format_exc())
            logging.error(msg)
            raise Exception(msg)
    
    def validate(self, type, name, version, category, user):
        """ Validate a package :
            - add it in the packages list
            - delete it from the submission list
        """
        logging.info("Validate a package from the submission list : {0}_{1} in version {2}".format(type, name, version))
        pkg_list = PackagesList()
        pkg = self.get_package(type, name, version)
        pkg['category'] = category
        pkg['validation_date'] = time.time()
        pkg['validation_by'] = user
        pkg_list.add(pkg)
        self.delete(type, name, version)
    
    def refuse(self, type, name, version, user, reason):
        """ Refuse a package :
            - add it in the refused packages list
            - delete it from the submission list
        """
        logging.info("Refuse a package in the submission list : {0}_{1} in version {2}".format(type, name, version))
        pkg_list = RefusedList()
        pkg = self.get_package(type, name, version)
        pkg['refused_date'] = time.time()
        pkg['refused_by'] = user
        pkg['refused_reason'] = reason
        pkg_list.add(pkg)
        self.delete(type, name, version)
    


class RefusedList():
    """ Class to manage the list of refused packages
    """

    def __init__(self):
        ### load the json
        # check if the file exists
        if os.path.isfile(REFUSED_PACKAGES_LIST):
            self.json = json.load(open(REFUSED_PACKAGES_LIST))
        else:
            self.json = []
        pass

    def list(self):
        """ Return the list of refused packages
        """
        data = self.json
        return sorted(data,key=itemgetter('type', 'name', 'version'))
    
    def add(self, data):
        """ add a package to the refused list
        """
        logging.info("Add a package in the refused list : {0}_{1} in version {2}".format(data["type"], data["name"], data["version"]))
        # we do not make any check about unicity here... this is just an history
        # add in the list
        self.json.append(data)
        self.save()
        msg = "Package refused from the submission list: {0}_{1} in version {2} (reason available online)".format(data["type"], data["name"], data["version"])
        logging.info(msg)
        tweet_message(msg)

    def delete(self, type, name, version):
        """ delete a package from the refused list
        """
        # TODO : no need currently
        pass

    def save(self):
        """ Save the list of refused packages
        """
        try:
            my_file = open(REFUSED_PACKAGES_LIST, "w")
            my_file.write(json.dumps(self.json, sort_keys = True))
            my_file.close()
        except:
            msg = "Unable to save the refused packages list : {0}".format(traceback.format_exc())
            logging.error(msg)
            raise Exception(msg)
    




class DevelopmentList():
    """ Class to manage the list of the 'in development' packages
    """

    def __init__(self):
        ### load the json
        # check if the file exists
        if os.path.isfile(IN_DEVELOPMENT_PACKAGES_LIST):
            self.json = json.load(open(IN_DEVELOPMENT_PACKAGES_LIST))
        else:
            self.json = []
        pass

    def list(self):
        """ Return the list of 'in development' packages
        """
        data = self.json
        return sorted(data,key=itemgetter('type', 'name', 'version'))
    
    def add(self, data):
        """ add a package to the 'in development' list
            Notice that the version is not needed/used
        """
        logging.info("New 'in development' package : {0}_{1} in version {2}".format(data["type"], data["name"], data["version"]))
        # check unicity
        for pkg in self.json:
            # we don't check the version as this is a non used data (package in dev, so no version)
            if pkg["type"] == data["type"] and pkg["name"] == data["name"]: 
                msg = "This package has already been validated by {0} (unique key is type/name)".format(pkg["submitter"])
                logging.error(msg)
                raise PackagesListError(msg)
                return
        # add in the list
        self.json.append(data)
        self.save()
        msg = "New package in the 'in development' list: {0}_{1}".format(data["type"], data["name"])
        logging.info(msg)
        tweet_message(msg)

    def delete(self, type, name):
        """ delete a package from the 'in development' list
            # the version is not used as a key as there are development packages
        """
        logging.info("Delete 'in development' package : {0}_{1}".format(data["type"], data["name"]))
        # Keep all packages excepting the one
        try:
            self.json_buf = []
            for pkg in self.json:
               if not (pkg["type"] == type and pkg["name"] == name):
                   self.json_buf.append(pkg)
            # add in the list
            self.json = self.json_buf
            self.save()
        except:
            msg = "Unable to remove from the 'in development' list : {0}".format(traceback.format_exc())
            logging.error(msg)
            raise Exception(msg)

    def save(self):
        """ Save the list of 'in development' packages
        """
        try:
            my_file = open(IN_DEVELOPMENT_PACKAGES_LIST, "w")
            my_file.write(json.dumps(self.json, sort_keys = True))
            my_file.close()
        except:
            msg = "Unable to save the 'in development' packages list : {0}".format(traceback.format_exc())
            logging.error(msg)
            raise Exception(msg)
    

