opcut
=====

`https://opcut.herokuapp.com/`

`opcut` is cutting stock problem optimizer
(`https://en.wikipedia.org/wiki/Cutting_stock_problem`) utilizing multiple
panels and guillotine cuts (end-to-end cuts). This project includes multiple
back-end optimizer implementations, command line front-end and single-page web
application front-end.


Runtime requirements
--------------------

* python >=3.6

Additional required python packages are listed in `requirements.txt`.


Development requirements
------------------------

* nodejs >=7
* yarn


Install
-------

    $ pip install opcut


Run
---

Running server (default listening address http://0.0.0.0:8080):

    $ opcut server

Running command line utility:

    $ opcut calculate ...

Additional command line arguments:

    $ opcut --help


Build
-----

Build tool used for `opcut` is pydoit (`http://pydoit.org/`). It can be
installed together with other python dependencies by running::

    $ pip install -r requirements.txt

For listing available doit tasks, use::

    $ doit list

Default task::

    $ doit

creates `dist` folder containing `opcut` distribution.


TODO
----

* global

    * create CONTRIBUTING

* optimizer

    * add additional algorithms
    * evaluate python implementations and do native rewrites if needed

* back-end

    * additional output formats

* front-end

    * additional GUI refactoring
