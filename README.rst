**This project is community maintained. Please continue to submit bugs and feature requests, though it's the community's responsibility to address them.**

.. image:: https://travis-ci.org/redcap-tools/PyCap.svg?branch=master
    :target: https://travis-ci.org/redcap-tools/PyCap
.. image:: https://badge.fury.io/py/PyCap.svg
    :target: https://badge.fury.io/py/PyCap

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
::

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
    >>> response = project.delete_record('1')

    # Export form event mappings
    >>> fem = project.export_fem()
    ...

    # Export Reports
    >>> reports = project.export_reports(['1','2'])

Installation
------------

Install with :code:`pip`
::

    $ pip install PyCap

Install extra requirements, which allows returning project data as a :code:`pandas.DataFrame`
::

    $ pip install PyCap[pandas]

Install from GitHub
::

    $ git clone git://github.com/redcap-tools/PyCap.git PyCap
    $ cd PyCap
    $ python setup.py install


Contributing
------------

1. Create a virtual environment and activate it
::

    $ python -m venv .venv
    $ source .venv/Scripts/activate

2. Install `pip-tools <https://github.com/jazzband/pip-tools/blob/master/README.rst>`_.
::

    $ pip install pip-tools

3. Install all project dependencies
::

    $ pip-sync requirements.txt dev-requirements.txt

4. Install the package, with a link to the source code. This ensures any changes you
make are immendiate available to test.
::

    $ python setup.py develop

5. Add your changes and make sure your changes pass all tests
::

    $ pytest

Finally, start a pull request!

Citing
------

If you use PyCap in your research, please consider citing the software:

    Burns, S. S., Browne, A., Davis, G. N., Rimrodt, S. L., & Cutting, L. E. PyCap (Version 1.0) [Computer Software].
    Nashville, TN: Vanderbilt University and Philadelphia, PA: Childrens Hospital of Philadelphia.
    Available from https://github.com/redcap-tools/PyCap. doi:10.5281/zenodo.9917
