from dmgweb_packages.common.config import CONFIG_FILE
from twitter import Api, TwitterError
import traceback
import os
import json

consumer_key = 'nVoQlpUFs7y5Wr4sh0jMmCxPF'
consumer_secret = 'ACIZdbtdgnSYsownfYzfJxVz31vWS2QSP0YqFg1gIyuOfBzTk2'
access_token =  '2832641026-Qczs1xAuXZlomypi2D6eRBaS2XTCGeRryeNK3b4'
access_token_secret = 's93HXvrd4ZZuqLRFq6QSAOO5Ozn2oIAE8fIZ5jF94sjXe'

class Tweet():

    def __init__(self):
        """ Get twitter configuration and create the twitter Api
        """
        ### load the json to get twitter config
        # check if the file exists
        if os.path.isfile(CONFIG_FILE):
            tmp_json = json.load(open(CONFIG_FILE))
            # test if tweeting is enabled or not....
            if not tmp_json['twitter']['enable']:
                print("We don't want to tweet!")
                return
            consumer_key = tmp_json['twitter']['consumer_key']
            consumer_secret = tmp_json['twitter']['consumer_secret']
            access_token_key = tmp_json['twitter']['access_token']
            access_token_secret = tmp_json['twitter']['access_token_secret']
        else:
            raise Exception("Twitter oauth configuration : unable to open or read file '{0}')".format(CONFIG_FILE))
            return

        ### Connect to twitter
        try:
            self.api = Api(consumer_key = consumer_key,
                           consumer_secret = consumer_secret,
                           access_token_key = access_token,
                           access_token_secret = access_token_secret)
            self.api.VerifyCredentials()
        except TwitterError:
            raise Exception("Unable to log in the twitter account : {0}".format(traceback.format_exc()))


    def publish(self, message, nb_try = 0):
        """ Just tweet
        """
        try:
            status = self.api.PostUpdate(message)
        except TwitterError as e:
            # duplicate message error...
            # let's try to add some random data at the end
            if e[0][0]['code'] == 187:
                if nb_try == 0:
                    message_addon = "Enjoy."
                elif nb_try == 1:
                    message_addon = "Have fun."
                elif nb_try == 2:
                    message_addon = ":)"
                elif nb_try == 3:
                    message_addon = ";)"
                elif nb_try == 4:
                    message_addon = ":D"
                else:
                    raise Exception("Too much duplicates for this message (3)....")
                new_message = "{0}. {1}".format(message, message_addon)
                self.publish(new_message, nb_try + 1)
        except:
            print("Unable to tweet : {0}".format(traceback.format_exc()))

def tweet_message(message):
    tweeter = Tweet()
    tweeter.publish(message)



if __name__ == "__main__":
    tweet_message("This will be cool (2)")

