.. image:: https://secure.travis-ci.org/sburns/PyCap.png?branch=master

Intro
=====

PyCap is a python module exposing the REDCap API through some helpful abstractions. Information about the REDCap project can be found at http://project-redcap.org/.

Available under the BSD (3-clause) license.

Features
--------

Currently, these API calls are available:

-   Export Records
-   Export Metadata
-   Import Records
-   Export File
-   Import File
-   Delete File
-   Export Users
-   Export Form Event Mappings

Events and Arms are automatically exported for longitudinal projects (see below).


Requirements
------------

-   requests (>= 1.0.0)

    ``$ easy_install requests``

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

    # Export form event mappings
    >>> fem = project.export_fem()
    ...

Installation
------------
::

    $ git clone git://github.com/sburns/PyCap.git PyCap
    $ cd PyCap
    $ python setup.py install

    OR

    $ pip install PyCap

TODO
----

-   Clean up some method defaults and prepare for the stable 1.0
