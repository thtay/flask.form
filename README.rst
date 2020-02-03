flask.form
======

Flask application that lets you take notes and add tags to the note.

Install
-------

Create a virtualenv and activate it:

.. code-block:: text

    $ python3 -m venv venv
    $ . venv/bin/activate

Or on Windows cmd:

.. code-block:: text

    $ py -3 -m venv venv
    $ venv\Scripts\activate.bat

Install Flaskr:

.. code-block:: text

    $ pip install -e .

Or if you are using the master branch, install Flask-SQLAlchemy from
source before installing Flaskr:

.. code-block:: text

    $ pip install -e ../..
    $ pip install -e .


Run
---

.. code-block:: text

    $ export FLASK_APP=flaskr
    $ export FLASK_ENV=development
    $ flask init-db
    $ flask run

Or on Windows cmd:

.. code-block:: text

    > set FLASK_APP=flaskr
    > set FLASK_ENV=development
    > flask init-db
    > flask run

Open http://127.0.0.1:5000 in a browser.
