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

Events and Arms are automatically exported for longitudinal projects (see below).


Requirements
------------

-   requests (> 0.6.4)

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

-   More Tests
-   File export and import
