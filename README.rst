**This project is community maintained. Please continue to submit bugs and feature requests, though it's the community's responsibility to address them.**

.. image:: https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml
.. image:: https://codecov.io/gh/redcap-tools/PyCap/branch/master/graph/badge.svg?token=IRgcPzANxU
    :target: https://codecov.io/gh/redcap-tools/PyCap
.. image:: https://badge.fury.io/py/PyCap.svg
    :target: https://badge.fury.io/py/PyCap
.. image:: https://img.shields.io/badge/code%20style-black-black
    :target: https://pypi.org/project/black/

Intro
=====

PyCap is a python module exposing the REDCap API through some helpful abstractions. Information about the REDCap project can be found at http://project-redcap.org/.

Available under the MIT license.

Documentation
-------------

Canonical documentation can be found on `ReadTheDocs <http://pycap.rtfd.org>`_.

Features
--------

Currently, these API calls are available:

-   Export Records
-   Export Metadata
-   Import Metadata
-   Delete Records
-   Import Records
-   Export File
-   Import File
-   Delete File
-   Export Users
-   Export Form Event Mappings
-   Export Reports

Events and Arms are automatically exported for longitudinal projects (see below).


Requirements
------------

-   requests (>= 1.0.0)

    ``$ pip install requests``

Usage
-----

.. code-block:: python

    >>> import redcap
    # Init the project with the api url and your specific api key
    >>> project = redcap.Project(api_url, api_key)

    # Export all data
    >>> all_data = project.export_records()

    # import data
    >>> data = [{'subjid': i, 'age':a} for i, a in zip(range(1,6), range(7, 13))]
    >>> num_processed = project.import_records(data)

    # For longitudinal projects, project already contains events, arm numbers
    # and arm names
    >>> print project.events
    ...
    >>> print project.arm_nums
    ...
    >>> print project.arm_names
    ...

    # Import files
    >>> fname = 'your_file_to_upload.txt'
    >>> with open(fname, 'r') as fobj:
    ...     project.import_file('1', 'file_field', fname, fobj)

    # Export files
    >>> file_contents, headers = project.export_file('1', 'file_field')
    >>> with open('other_file.txt', 'w') as f:
    ...     f.write(file_contents)

    # Delete files
    >>> try:
    ...     project.delete_file('1', 'file_field')
    ... except redcap.RedcapError:
    ...     # This throws if an error occured on the server
    ... except ValueError:
    ...     # This throws if you made a bad request, e.g. tried to delete a field
    ...     # that isn't a file

    # Delete record
    >>> response = project.delete_record(['1'])

    # Export form event mappings
    >>> fem = project.export_fem()
    ...

    # Export Reports
    >>> reports = project.export_reports(['1','2'])

Installation
------------

Install with :code:`pip`

.. code-block:: sh

    $ pip install PyCap

Install extra requirements, which allows returning project data as a :code:`pandas.DataFrame`

.. code-block:: sh

    $ pip install PyCap[pandas]

Install from GitHub

.. code-block:: sh

    $ pip install https://github.com/redcap-tools/PyCap/archive/master.zip


Contributing
------------


1. Install `poetry <https://python-poetry.org/docs/master/#installation>`_

.. code-block:: sh
    
    $ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -


2. Install all project dependencies (including development/optional dependencies).

.. code-block:: sh

    $ poetry install -E data_science

3. Add your changes and make sure your changes pass all tests.

.. code-block:: sh

    $ poetry run pytest

If you make changes to the dependencies you'll need to handle
them with `poetry add/remove <https://python-poetry.org/docs/master/basic-usage/#installing-dependencies>`_
and update the :code:`requirements.txt` with
`poetry export <https://python-poetry.org/docs/master/cli/#export>`_ for the CI to run
(until I figure out the best way to actually run :code:`poetry` in CI)

.. code-block:: sh

    $ poetry export -f requirements.txt --output requirements.txt --dev -E data_science

Finally, start a pull request!

Citing
------

If you use PyCap in your research, please consider citing the software:

    Burns, S. S., Browne, A., Davis, G. N., Rimrodt, S. L., & Cutting, L. E. PyCap (Version 1.0) [Computer Software].
    Nashville, TN: Vanderbilt University and Philadelphia, PA: Childrens Hospital of Philadelphia.
    Available from https://github.com/redcap-tools/PyCap. doi:10.5281/zenodo.9917
