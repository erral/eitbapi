eitbapi
=======

A pyramid_ app to expose an API for `EITB Nahieran`_


Installation
=============

To run and install localy, create a virtualenv first and then::

  $ pip install -e .
  $ pserver development.ini --reload

Add a Redis_ instance to provide caching of results (optional)
----------------------------------------------------------------

Install redis and provide its url as an environment variable called **REDIS_URL**.
Doing that the application will save the results on it.


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
