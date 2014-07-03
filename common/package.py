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




### package related configuration items

JSON_FILE = "info.json"
ICON_FILE = "design/icon.png"
ICONS_DIR = "data/icons/"
PACKAGES_LIST = "data/packages.json"
SUBMITTED_PACKAGES_LIST = "data/submitted_packages.json"
REFUSED_PACKAGES_LIST = "data/refused_packages.json"


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

    def download(self):
        """ Download the package to a temporary path for analysis
        """
        # check if this is an url
        if not URL_REGEXP.search(self.url):
            return False, "{0} is not a valid url".format(self.url)


        try:

            #response = requests.get(self.url)

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

        except: 
            return False, "Error while downloading the package : {0}".format(traceback.format_exc())
        return True, None


    def get_info_json(self):
        """ Get the info.json file from the zip
        """
        # get the hash of the file to check it has not change
        hash_sha256 = hashlib.sha256(open(self.downloaded_file, 'rb').read()).hexdigest()
        print hash_sha256 
        
        # check the zip file contains what we need
        with zipfile.ZipFile(self.downloaded_file, 'r') as myzip:
            # test the zip file
            testzip = myzip.testzip()
            if testzip != None:
                return False, "The zip seems not to be good for the file : {0}".format(testzip)
          

            # security!!!!! check if there is no .. or / in files path
            for fic in myzip.namelist():
                if fic[0:1] == "/" or fic[0:2] == "..":
                    return False, "Security issue ! The zip contains some files with a path starting by '/' or '..'"

            # we assume that the first item of the list is the master directory in the zip and so the info.json file is under it
            try:
                root_dir = myzip.namelist()[0]
            except:
                return False, "Error while looking in the zip file : {0}".format(traceback.format_exc())
            json_file = os.path.join(root_dir, JSON_FILE)
            try:
                fp_json = myzip.open(json_file, 'r')
            except KeyError:
                return False, "There is no file named '{0}' in this zip archive!".format(json_file)
            self.json_data = json.load(fp_json)
            self.json_data["hash_sha256"] = hash_sha256
            print self.json_data

            # extract the package icon
            for member in myzip.namelist():
                print member
            source = myzip.open(os.path.join(root_dir, ICON_FILE))
            target = file(os.path.join(ICONS_DIR, "{0}_{1}_{2}.png".format(self.json_data['identity']['type'], self.json_data['identity']['name'], self.json_data['identity']['version'])), "wb")
            with source, target:
                shutil.copyfileobj(source, target)
 

            return True, None

        # TODO : validate json
        # how to get the PackageJson library easily ?

    def get_json(self):
        return self.json_data


    def delete_downloaded_file(self):
        """ Delete the temporary file
        """
        try:
            os.unlink(self.downloaded_file)
        except:
            print("ERROR : unable to delete {0}".format(self.downloaded_file))
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
        print("Packages : {0}".format(self.json))
        pass

    def list(self):
        """ Return the list of submitted packages
        """
        return self.json
    
    def add(self, data):
        """ add a package to the submission list
        """
        # check unicity
        for pkg in self.json:
           if pkg["type"] == data["type"] and pkg["name"] == data["name"] and  pkg["version"] == data["version"]:
               raise PackagesListError("This package has already been validated by {0} (unique key is type/name/version)".format(pkg["submitter"]))
               return
        # add in the list
        self.json.append(data)
        self.save()

    def delete(self, type, name, version):
        """ delete a package from the submission list
        """
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
            raise error("Unable to remove from the packages list : {0}".format(traceback.format_exc()))

    def save(self):
        """ Save the list of packages
        """
        try:
            my_file = open(PACKAGES_LIST, "w")
            my_file.write(json.dumps(self.json))
            my_file.close()
        except:
            raise error("Unable to save the packages list : {0}".format(traceback.format_exc()))
    




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
        print("Submission list : {0}".format(self.json))

    def list(self):
        """ Return the list of submitted packages
        """
        return self.json
    
    def add(self, data):
        """ add a package to the submission list
        """
        # check unicity
        for pkg in self.json:
           if pkg["type"] == data["type"] and pkg["name"] == data["name"] and  pkg["version"] == data["version"]:
               raise SubmissionError("This package has already been submitted by {0} (unique key is type/name/version)".format(pkg["submitter"]))
               return
        # add in the list
        print("DATA : {0}".format(data))
        self.json.append(data)
        self.save()

    def delete(self, type, name, version):
        """ delete a package from the submission list
        """
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
            raise error("Unable to remove from the submission list : {0}".format(traceback.format_exc()))

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
            my_file.write(json.dumps(self.json))
            my_file.close()
        except:
            raise error("Unable to save the submission list : {0}".format(traceback.format_exc()))
    
    def validate(self, type, name, version, user):
        """ Validate a package :
            - add it in the packages list
            - delete it from the submission list
        """
        pkg_list = PackagesList()
        pkg = self.get_package(type, name, version)
        pkg['validation_date'] = time.time()
        pkg['validation_by'] = user
        pkg_list.add(pkg)
        self.delete(type, name, version)
    
    def refuse(self, type, name, version, user, reason):
        """ Refuse a package :
            - add it in the refused packages list
            - delete it from the submission list
        """
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
        print("Refused packages : {0}".format(self.json))
        pass

    def list(self):
        """ Return the list of refused packages
        """
        return self.json
    
    def add(self, data):
        """ add a package to the refused list
        """
        # we do not make any check about unicity here... this is just an history
        # add in the list
        self.json.append(data)
        self.save()

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
            my_file.write(json.dumps(self.json))
            my_file.close()
        except:
            raise error("Unable to save the refused packages list : {0}".format(traceback.format_exc()))
    
