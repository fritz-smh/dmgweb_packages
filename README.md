dmgweb_packages
===============

Domogik packages manager


Installation
------------

First, configure GitHub to allow the Oauth!

Go on https://github.com/settings/applications/new to register your application and fill the form :

* Application name: dmgwev-package
* Homepage url: http://my-repo.com/github-callback
* Application description: ....
* Authorization callback URL: http://my-repo.com/github-callback

Click on "Register application". The tokens *client_id* and *client_secret* are generated. Keep them somewhere.


Install some prerequisites on the server:

    apt-get install realpath
    pip install GitHub-Flask
    pip install Flask-SQLAlchemy
    pip install Flask-Bootstrap
    pip install Flask-WTF
    pip install Flask-Babel
    pip install Frozen-Flask
    pip install magic
    pip install python-twitter
    pip install uwsgi


On the server, clone the repository: 

    git clone https://github.com/fritz-smh/dmgweb_packages.git

Create needed folder:

    cd dmgweb_packages
    mkdir logs
    mkdir -p data/icons

Create a configuration file:

    cp examples/config.json.sample config.json

Then, fill the configuration file **config.json** 

    {
      "server_ip" : "0.0.0.0",
      "server_port" : "80",
      "github" :
        {
          "skip" : false,
          "client_id" : "xxxx",
          "client_secret" : "xxxx",
          "callback_url" : "http://something.com/github-callback"
        },
      "twitter" :
        {
          "enable" : true,
          "consumer_key" : "xxxx",
          "consumer_secret" : "xxxx",
          "access_token" :  "xxxx-Qczs1xAuXZlomypi2D6eRBaS2XTCGeRryeNK3b4",
          "access_token_secret" : "xxxx"
        },
      "root_repository" : "http://xxxx/",
      "domogik_releases" : [
        "0.4.0", "0.4.1", "0.4.2", "0.5.0", "0.5.1", "0.5.2", "0.6.0"
      ]
    }

The **skip** part in the **github** part allow to skip the Github authentication for development purpose. It should be set to false in production!!!!

The following example assume the current user ($LOGNAME) is the user which will run the tool.

Create an **init.d** file. From the *dmgweb_packages* folder, run as **root** :

    THE_USER=$(echo $LOGNAME)
    sudo sed "s#___INSTALL_PATH___#$PWD/../#g" examples/init.sample > /etc/init.d/dmgweb_packages
    sudo sed -i "s#___USER___#${THE_USER}#g" /etc/init.d/dmgweb_packages 
    sudo chmod a+x /etc/init.d/dmgweb_packages


Prerequisite : twitter account
------------------------------

A twitter account is needed to publish the repository updates (new package, ....)

* Create a twitter account
* Go on https://apps.twitter.com/app/new
* Grab the key and access tokens

Files and folders generated
---------------------------

Some files and folders are generated by the application:

* a sqlite database to store authentication informations : ./github-flask.db
* logs on the folder ./logs
* json files for the packages lists, icons, tgz of the website mirror in ./data

The folder **data** is the important one to backup !


Generate the mirror tgz (which is also a backup!!!)
---------------------------------------------------

To allow users creating mirrors of the website, please add this in the crontab :

    0 0 * * * /path/to/dmgweb_packages/mirror.sh > /path/to/dmgweb_packages/log/dmgweb_package_mirror_$(date "+%Y%m%d_%H%M").log

This will create each night a file **data/mirror.tgz** which is a static version of the website.

**Please notice that downloading the mirror.tgz file is also a backup action!** The *mirorr.sh* script include also in the tgz a copy of all the json files which contains the packages informations.


Restore from the mirror.tgz backup
----------------------------------

* Install dmgweb_packages as usual
* Extract the mirror.tgz somewhere
* in *dmgweb_packages/data/icons* copy the content or *mirror/icons/*
* in *dmgweb_packages/data/* copy the content or *mirror/save_json/*

Restore is done !

Deploy a mirror tgz on a web server (nginx)
-------------------------------------------

Extract the tgz file somewhere, for example : 

    cd /tmp
    rm -f mirror.tgz   # in case it exists
    wget http://the-repo.com/data/mirror.tgz
    cd /var/log/www/repo/
    tar xvzf mirror.tgz

Configure the webserver (nginx here) :

    server {
        ...
        default_type text/html;
    
        location / {
            index;
            ...
        }
        ...
    }

