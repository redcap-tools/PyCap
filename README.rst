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
    >>> all_data = project.export_records()
    
    # filter your data
    >>> q = redcap.Query('age', {'ge':12})
    >>> subset = project.filter(q)
    
    # import data
    >>> data = [{'subjid': i, 'age':a} for i, a in zip(range(1,6), range(7, 13))]
    >>> num_processed = project.import_records(data)
    
Installation
------------
::

    $ git clone git://github.com/VUIIS/PyCap.git PyCap
    $ cd PyCap
    $ python setup.py install
    
    OR
    
    $ easy_install PyCap

TODO
----

-   More Tests
-   File export and import
