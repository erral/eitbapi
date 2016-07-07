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

Link the **etc/nginx-vh-conf** file to your nginx's configuration directory
(usually /etc/nginx/conf.d)

Add a Redis_ instance to provide caching of results (optional)
----------------------------------------------------------------

Install redis and provide its url as an environment variable called **REDIS_URL**.
Doing that the application will save the results on it.


Deployment on Heroku
====================

You can deploy this package on Heroku_. To do so, first create an account at
Heroku_ and install `Heroku Toolbelt`_ and login for the first time from the
console::

    $ heroku login

Now you are ready to create the application on Heroku:

- Clone this repository::

    $ git clone git@github.com:erral/eitbapi
    $ cd eitbapi

- Create the heroku app::

    $ heroku create


- (**optional**) Add a free-tier Redis_ instance for caching the results from `EITB Nahieran`_::

    $ heroku addons:create heroku-redis:hobby-dev

- Deploy the code to Heroku::

    $ git push heroku master

- Open the web browser pointing to the application::

    $ heroku open

.. unicode:: U+1F64C U+1F64C U+1F64C U+1F64C 

.. _pyramid: http://docs.pylonsproject.org/projects/pyramid
.. _`EITB Nahieran`: http://www.eitb.tv
.. _Heroku: https://www.heroku.com
.. _`Heroku Toolbelt`: https://toolbelt.heroku.com/
.. _Redis: http://redis.io
