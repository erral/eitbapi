eitbapi
=======

A pyramid_ app to expose an API of EITB Nahieran


Installation
=============

Common parts::

  $ git clone git@bitbucket.org:codesyntax/eitbapi
  $ virtualenv .
  $ ./bin/pip install zc.buildout
  $ ./bin/buildout -vv


To run in development mode::

  $ ./bin/pserve development.ini --reload

To run in production mode::
  $ ./bin/supervisord

Link the etc/nginx-vh-conf file to your nginx's configuration directory
(usually /etc/nginx/conf.d)
