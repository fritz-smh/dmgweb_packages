import json
import os

PWD = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = "{0}/../config.json".format(PWD)


class Config:
    def __init__(self):
        ### load the json
        # check if the file exists
        if os.path.isfile(CONFIG_FILE):
            self.json = json.load(open(CONFIG_FILE))
        else:
            raise Exception("Configuration : unable to open or read file '{0}')".format(CONFIG_FILE))

    def _get_config_item(self, item):
        """ generic fucntion
        """
        try:
            return self.json[item]
        except KeyError:
            return None
    
    
    def get_domogik_releases(self):
        return self._get_config_item('domogik_releases')
    
    def get_api_token(self):
        return self._get_config_item('api_token')
    
    def get_server_ip(self):
        return self._get_config_item('server_ip')
    
    def get_server_port(self):
        try:
            return int(self._get_config_item('server_port'))
        except:
            return 0
    
    def get_root_repository_url(self):
        return self._get_config_item('root_repository')
    
    def get_metrics_url(self):
        return self._get_config_item('metrics')['url']
    
    def get_metrics_token(self):
        return self._get_config_item('metrics')['token']
    
    def get_review_command(self):
        return self._get_config_item('review')['command']
    
        
