opcut
=====

`https://opcut.herokuapp.com/`

`opcut` is cutting stock problem optimizer
(`https://en.wikipedia.org/wiki/Cutting_stock_problem`) utilizing multiple
panels and guillotine cuts (end-to-end cuts). This project includes:

    * multiple back-end optimizer implementations
    * command line front-end
    * REST service API (OpenAPI definition)
    * single-page web application front-end


Runtime requirements
--------------------

* python >=3.8


Development requirements
------------------------

* nodejs >=7
* yarn


Install
-------

::

    $ pip install opcut

.. note::

    on Ubuntu, if pycairo is not available, additional
    ``apt install gcc pkg-config libcairo2-dev python3-dev`` is required

.. note::

    Windows distribution, with embedded python, is available at
    `https://github.com/bozokopic/opcut/releases`


Run
---

Running server (default listening address http://0.0.0.0:8080)::

    $ opcut server

Running command line utility::

    $ opcut calculate ...
    $ opcut generate_output ...

Additional command line arguments::

    $ opcut --help


Build
-----

Build tool used for `opcut` is pydoit (`http://pydoit.org/`). It can be
installed together with other python dependencies by running::

    $ pip install -r requirements.pip.dev.txt

For listing available doit tasks, use::

    $ doit list

Default task::

    $ doit

creates wheel package inside `build` directory.


TODO
----

* global

    * create CONTRIBUTING

* optimizer

    * add additional algorithms
    * evaluate python implementations and do native rewrites if needed

* back-end

    * additional output formats


License
-------

opcut - cutting stock problem optimizer
Copyright (C) 2017-2021  Bozo Kopic

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
