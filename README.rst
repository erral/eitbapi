eitbapi
=======

A pyramid_ app to expose an API of `EITB Nahieran`_


Installation
=============

Common parts. It will install buildout and download the dependencies::

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

.. _pyramid: http://docs.pylonsproject.org/projects/pyramid
.. _`EITB Nahieran`: http://www.eitb.tv
