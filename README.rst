.. _cutting stock problem: https://en.wikipedia.org/wiki/Cutting_stock_problem
.. _GitHub releases: https://github.com/bozokopic/opcut/releases
.. _AUR package: https://aur.archlinux.org/packages/opcut
.. _PyPI project: https://pypi.org/project/opcut
.. _Docker image: https://hub.docker.com/r/bozokopic/opcut

opcut
=====

`<https://opcut.kopic.xyz/>`_

`opcut` is `cutting stock problem`_ optimizer utilizing multiple
panels and guillotine cuts (end-to-end cuts). This project includes:

* multiple back-end optimizer implementations
* command line front-end
* REST service API (OpenAPI definition)
* single-page web application front-end

Git repository is available at `<https://github.com/bozokopic/opcut.git>`_.

Public instance `<https://opcut.kopic.xyz/>`_ is constrained with limited
resources and should be used only for functionality evaluation purposes.
In case of complex and repetitive calculations, please consider running
self hosted instance.


Runtime requirements
--------------------

* python >=3.10

.. note::

    on Ubuntu, if pycairo is not available, additional
    ``apt install gcc pkg-config libcairo2-dev`` is required


Install
-------

Archlinux
'''''''''

`opcut` is available as `AUR package`_::

    $ yay -S opcut


Windows
'''''''

Windows distribution, with embedded python, is available at `GitHub releases`_.

This archive contains `opcut-server.cmd`, which can be used for running
server application, and `opcut.cmd` as generic `opcut` action launcher.


Python wheel
''''''''''''

Opcut is available as `PyPI project`_::

    $ pip install opcut


Docker
''''''

`opcut` server is available as `Docker image`_::

    $ docker run -p 8080:8080 bozokopic/opcut


Usage
-----

`opcut` command is interface for execution of three distinct actions:

* `opcut calculate ...`

    Calculation of cutting stock problem. Input parameters and result is
    formatted as JSON data (JSON, YAML or TOML).

* `opcut generate ...`

    Generate output representation (SVG, PDF, ...) based on calculation
    result.

* `opcut server ...`

    Run HTTP server providing single-page web application interface and
    OpenAPI interface (default listening address is http://0.0.0.0:8080).

For additional command line arguments and documentation, run::

    $ man 1 opcut

JSON schema describing data structures is available at `<schemas/opcut.yaml>`_.

OpenAPI definition is available at `<schemas/openapi.yaml>`_.


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
* npm


Build
-----

Build tool used for `opcut` is pydoit (`http://pydoit.org/`). It can be
installed together with other python dependencies by running::

    $ pip install -r requirements.pip.txt

For listing available doit tasks, use::

    $ doit list

Default task::

    $ doit

creates wheel package inside `build` directory.


TODO
----

* unit tests
* changelog
* mailing list
* roadmap


Contributing
------------

This project is currently in "proof of concept" state and is not yet
recommended for production usage.

Any kind of help in development of this project is appreciated.

Issues and feature requests can be submitted to
`issue tracker <https://github.com/bozokopic/opcut/issues>`_.

Repository changes can be sent as patches over email (Github pull request are
also acceptable until dedicated mailing list is set up). Changes containing
new functionality or other significant changes should be discussed prior
to sending patch.

For any questions regarding this project, contact me at bozo@kopic.xyz.


License
-------

opcut - cutting stock problem optimizer

Copyright (C) 2017-2025 Bozo Kopic

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
