dmgweb_packages
===============

Domogik packages manager


Installation
------------

First, configure GitHub to allow the Oauth!

Go on https://github.com/settings/applications/new to register your application and fill the form :

* Application name: dmgwev-package
* Homepage url: http://les-cours-du-chaos.hd.free.fr/
* Application description: ....
* Authorization callback URL: Authorization callback URL

Click on "Register application". The tokens *client_id* and *client_secret* are generated. Keep them somewhere.


Install some prerequisites on the server:

    pip install GitHub-Flask
    pip install Flask-SQLAlchemy
    pip install Flask-Bootstrap
    pip install Frozen-Flask

On the server, clone the repository: 

    git clone https://github.com/fritz-smh/dmgweb_packages.git

Then, fill the configuration file **config.json** 


    {
      "github" : 
        {
          "client_id" : "c5a32b7a5e965432febd",
          "client_secret" : "c543f3423a32cC435454353450674a076dd12ca7",
          "callback_url" : "http://my-repo.com/github-callback"
        },
      "root_repository" : "http://repo-dev.domogik.org/",
      "categories" : 
        [
          { "id" : "nightly",    "name" : "Nightly",  "is_nightly" : true,  "is_obsolete" : false },
          { "id" : "stable",     "name" : "Stable",   "is_nightly" : false, "is_obsolete" : false },
          { "id" : "oldstable",  "name" : "Obsolete", "is_nightly" : false, "is_obsolete" : true }
        ],
      "dashboard" :
        {
          "components" : 
            [
              { "label" : "Domogik (master)",     "url_build_status" : "https://travis-ci.org/domogik/domogik.png?branch=master" },
              { "label" : "Domogik (0.3)",        "url_build_status" : "https://travis-ci.org/domogik/domogik.png?branch=0.3" }
            ]
        }
    }


TODO : continue :)


Files and folders generated
---------------------------

Some files and folders are generated by the application:

* a sqlite database to store authentication informations : ./github-flask.db
* logs on the folder ./logs
* json files for the packages lists, icons, tgz of the website mirror in ./data

The folder **data** is the important one to backup !


Generate the mirror tgz
-----------------------

To allow users creating mirrors of the website, please add this in the crontab :

    0 0 * * * /path/to/dmgweb_packages/mirror.sh > /path/to/dmgweb_packages/log/dmgweb_package_mirror_$(date "+%Y%m%d_%H%M").log

This will create each night a file **data/mirror.tgz** which is a static version of the website.


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

