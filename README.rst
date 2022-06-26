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

.. note::

    on Ubuntu, if pycairo is not available, additional
    ``apt install gcc pkg-config libcairo2-dev python3-dev`` is required


Install
-------

::

    $ pip install opcut

.. note::

    Windows distribution, with embedded python, is available at
    `https://github.com/bozokopic/opcut/releases`


Usage
-----

`opcut` command is interface for execution of three distinct actions:

    * `opcut calculate ...`

        Calculation of cutting stock problem. Input parameters and result is
        formated as JSON data (JSON, YAML or TOML).

    * `opcut generate ...`

        Generate output representation (SVG, PDF, ...) based on calculation
        result.

    * `opcut server ...`

        Run HTTP server providing single-page web application interface and
        OpenAPI interface.
        (default listening address is http://0.0.0.0:8080).

For additional command line arguments, run ``opcut --help`` or
``opcut <action> --help``.


`opcut calculate`
'''''''''''''''''

Example::

    $ opcut calculate --input-format yaml --output result.json << EOF
    cut_width: 1
    panels:
        panel1:
            width: 100
            height: 100
    items:
        item1:
            width: 10
            height: 10
            can_rotate: false
    EOF


`opcut generate`
''''''''''''''''

Example::

    $ opcut generate --output output.pdf result.json


`opcut server`
''''''''''''''

Example::

    $ opcut server


Development requirements
------------------------

* C99 compiler (gcc, clang, ...)
* nodejs >=7
* yarn


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


JSON Schema
-----------

.. literalinclude:: schemas/opcut.yaml
    :language: yaml


OpenAPI
-------

.. literalinclude:: schemas/openapi.yaml
    :language: yaml


License
-------

opcut - cutting stock problem optimizer

Copyright (C) 2017-2022 Bozo Kopic

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
