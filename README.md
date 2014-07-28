dmgweb_packages
===============

Domogik packages manager


Installation
------------

On a server, clone the repository: ::

    git clone https://github.com/fritz-smh/dmgweb_packages.git

Then, fill the configuration file *config.json* ::


    {
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

