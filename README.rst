optcut
======

`https://opcut.herokuapp.com/`

`optcut` is cutting stock problem optimizer
(`https://en.wikipedia.org/wiki/Cutting_stock_problem`) utilizing multiple
panels and guillotine cuts (end-to-end cuts). This project includes multiple
back-end optimizer implementations and single-page web application front-end.


Runtime requirements
--------------------

* python >=3.6

Additional required python packages are listed in `requirements.txt`.


Development requirements
------------------------

* nodejs >=7
* yarn


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
    * cleanup package.json
    * cleanup webpack.config.js
    * write setup.py

* optimizer

    * evaluate research papers and proposed algorithms
    * define optimizer api
    * implement multiple algorithms in python
    * evaluate python implementations and do native rewrites is needed

* back-end

    * define json schemas and communication interface between back-end and
      front-end
    * basic backend implementation in python
    * additional functionality (multiple output formats)

* front-end

    * implement communication with back-end
    * additional GUI refactoring
