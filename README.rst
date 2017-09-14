eitbapi
=======

A pyramid_ app to expose an API for `EITB Nahieran`_ (unofficial)

.. image:: https://travis-ci.org/erral/eitbapi.svg?branch=master
    :target: https://travis-ci.org/erral/eitbapi

.. image:: https://coveralls.io/repos/github/erral/eitbapi/badge.svg
    :target: https://coveralls.io/github/erral/eitbapi


View API online
===============

https://still-castle-99749.herokuapp.com/


Installation
=============

To run and install localy, create a virtualenv first and then::

  $ pip install -r requirements.txt
  $ pip install -e .
  $ pserver development.ini --reload


Deployment on Heroku
====================

You can deploy this app on Heroku_. To do so, first create an account at
Heroku_ and install `Heroku Toolbelt`_ and login for the first time from the
console::

    $ heroku login

Now you are ready to create the application on Heroku:

- Clone this repository::

    $ git clone git@github.com:erral/eitbapi
    $ cd eitbapi

- Create the heroku app::

    $ heroku create

- Deploy the code to Heroku::

    $ git push heroku master

- Open the web browser pointing to the application::

    $ heroku open

.. unicode:: U+1F64C U+1F64C U+1F64C U+1F64C



.. _pyramid: http://docs.pylonsproject.org/projects/pyramid
.. _`EITB Nahieran`: http://www.eitb.tv
.. _Heroku: https://www.heroku.com
.. _`Heroku Toolbelt`: https://toolbelt.heroku.com/
