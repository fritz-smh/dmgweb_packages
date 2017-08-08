In french, sorry ;)

Objectifs de la version
=======================

Conserver :

* la génération statique pour diffusion (et permettre les mirroirs)
* l'authenfication GitHub pour soumettre des packages


Changements :

* séparation entre la partie admin et la partie publique
* identification sur la partie admin via Github (pour gestion login + mdp)
* gestion des autorisations via login en 'fait maison'
* 2 types d'accès sur la partie admin :

  * public (sous réserver d'auth Github) : soumission d'un package
  * privé (auth Github + autorisation) : gestion des packages

* Critère de rangement des packages :

  * Il n'y a plus de dépôts (stable, obsolète, etc), il y a des status. Les vues qui affichents les packages filtreront sur des status
  * Version min de Domogik compatibles
  * Type de package

Donnees : 

* un json par package (qui contient les differentes versions)
* un json agrege qui contient tous les packages, utilise uniquement pour l'affichage
* a chaque modif d'un json, le json agrege est reconstruit

* un dossier d'icones
* un dossier qui contient les rapports de review



Workflow d'un package
=====================

Statut :
```
     o
    -+-    --------------------------->   NEW_PACKAGE_SUBMITTED     // package submitted
     |                                       |               |
    / \                                      |review ok      \--------------------> INVALID    // automatic review failed or manuel review KO
                                             |               /    review ko
     |                                       v               |
     |                                    NEW_PACKAGE_TO_REVIEW     // automatic review ok, need a manuel review as this is a totally new package
     |                                       |
     v                                       |manuel review ok
 NEW_RELEASE_SUBMITTED                       v
  |           // an existing package      NEW_PACKAGE    // automatic and manuel review ok. As this is a new package, we should do some communication on it
  |              new release                 |
  |auto review ok                            |communication ready/done
  v                                          v
 NEW_RELEASE --------------------------->  BETA      // package reviewed but still needs some long testing. Or package that depends on an unstable service (yahoo weather)
  |            small manuel review ok      |  ^
  |                                        |  |      // to define : when a package goes from BETA to STABLE and fallback from STABLE to BETA ?
  |small manuel review KO                  v  |
  v                                       STABLE     // package validated by several users
 INVALID                                     |
                                             |manual action for now
                                             v
                                          ARCHIVED   // old packages that may be still usable in current or old Domogik release
                                             |
                                             |manual action for now
                                             v
                                          DELETED    // old packages that can't be used anymore (broken due to an online webservice change, ...)
   
```

Workflow :

```
 [ Soumission initiale ] ---> [ Lancement review ] ----> [ Message au développeur avec le rapport ]
                                    |                ko
                                    |ok       
                                    v          
          [ Enregistrement avec tag 'new package to check' ]
                           |
                           v
          [ Envoi notification aux admins et reviewers ]
                           |
                           | @attente action manuelle admin ou reviewer
                           v
          [ Review manuelle du package ]  // liste des actions à réaliser affichées : icônes, tests, ...
                           |
                           | ---------->  [ Envoi d'un message au développeur avec des raisons ]
                           |     ko
                        ok |
                           v
          [ Package validé avec tag 'new package' ]
                           |
                           v
          [ Envoi d'une communication automatique : tweeter, irc ]
                           |
                           v
          [ Envoi notification aux admins et reviewer pour faire un article dans le blog ]
                           |
                           | @attente votes
                           v                       non
                   [ N votes ok et 0 votes KO ? ] -----> [ TODO : définir actions ]
                           |
                           | oui
                           v
                   [ Tag 'new package' supprimé' ]
                   [ Tag 'stable' ajouté' ]
                                                          
                                                          
                                                          
                                                          
```

TODO : quid des packages comme weather qui ne peuvent etre mis en stable (cf cloud)





Nouvel essai :

                [0]---------------------> ko ------> delete
                 |                        ^
           auto review ok                 |
                 |                        |
                 |------------------------+ // la raison du ko sera dans les notes
                 v                        ^
         manual review ok                 |
                 |                        |
                 |------------------------+ 
                 v                        ^
                beta                      |
                ^  |                      |
                |  |----------------------+ 
                |  v
               stable
                 |
               archive
                 |
               delete


Données
=======

Il y a un fichier json par package, dans un dossier commun.

Exemple : 

```

{
  'package_id' : 'plugin-weather',
  'author_email' : 'mail@fourni@alasoumissioninitiale',
  'site' : 'https://github.com/fritz-smg/domogik-plugin-weather',
  'is_new' : true,    // values : true, false
  'releases' : 
    [
      {
        'release' : '1.1',
        'url_package' : 'http://......',
        'url_documentation' : 'http://......',
        'url_tests' : 'http://......',
        'url_review' : '/reviews/plugin_weather_1.1.html',
        'status' : 'SUBMITTED',    // values : .....
      },
      ...
    ],
  'notes' : 
    [
      {
        'timestamp' : 1234567890,
        'author' : 'fritz',
        'data' : 'super plugin!'
    ],
```




Lots
====

Lot 1
-----

- Structure de données (arbo)
  - fichiers des packages
  - icones
  - rapport de review en html par package par version
- Fonction de login avec oauth debrayable en dev
- Page de creation d'un nouveau package
  - saisie url site
  - saisie email auteur
- Init d'un nouveau package
- Page de soumission d'une version de package
  - liste des packages existant
  - url de la version du package
  - Soumission : la version est mise dans une file 'a traiter'
  - Lancement de la revue auto, generation du rapport, ajout du lien vers le rapport dans la release du package + ajout note auto
  - Envoi mail sur le résultat de la review
- Page de consultation des packages
  - liste des packages
    - liste des releases
    - liste des notes
    - lien pour soumettre une nouvelle version






