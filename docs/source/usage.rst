Usage
=====

.. _installation:

Installation
------------

To use Python REST, first install it using pip:

.. code-block:: console

   (.venv) $ pip install pythonrest3

Checking Version
----------------

To retrieve the installed version,
you can use the ``pythonrest version`` command:

Generating the REST API
-----------------------

Generate APIs based on MySQL databases:


``pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>``


Generate APIs based on Postgres databases:

``pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public``

Generate APIs based on SQLServer databases:

``pythonrest generate --sqlserver-connection-string mssql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>``

Generate APIs based on DariaDB databases:

``pythonrest generate --mariadb-connection-string mariadb://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>``

Generate APIs based on Aurora MySQL databases:

``pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>``

Generate APIs based on Aurora Postgres databases:

``pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public``

