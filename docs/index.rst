.. PyCap documentation master file, created by
   sphinx-quickstart on Thu Jan 12 14:09:09 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyCap
=====

PyCap is an interface to the `REDCap <http://www.project-redcap.org>`_ Application Programming Interface (API). PyCap is designed to be a minimal interface exposing all required and optional API parameters. Our hope is that it makes simple things easy & hard things possible.

Installation
------------

Install the latest version with `pip <https://pypi.python.org/pypi/pip>`_::

    $ pip install PyCap

If you want to load REDCap data into `pandas <https://github.com/redcap-tools/PyCap>`_ dataframes, this will make sure you have pandas installed::

    $ pip install 'PyCap[pandas]'

To install the bleeding edge from the github repo, use the following::

    $ pip install -e git+https://github.com/redcap-tools/PyCap.git#egg=PyCap

Philosophy
----------

The REDCap API is pretty simple. There is no built-in search or pagination, for example. However, it does expose all the functionality required to build advanced data management services on top of the API.

In the same way, PyCap is minimal by design. It doesn't do anything fancy behind the scenes and will not prevent you from shooting yourself in the foot. However, it should be very easy to understand and mentally-map PyCap functionality to the REDCap API.

License
-------

PyCap is licensed under the `MIT license <http://opensource.org/licenses/MIT>`_.

Citing
------

If you use PyCap in your research, please consider citing the software:

    Burns, S. S., Browne, A., Davis, G. N., Rimrodt, S. L., & Cutting, L. E. PyCap (Version 1.0) [Computer Software].
    Nashville, TN: Vanderbilt University and Philadelphia, PA: Childrens Hospital of Philadelphia.
    Available from https://github.com/redcap-tools/PyCap. doi:10.5281/zenodo.9917


Contents:

.. toctree::
   :maxdepth: 2

   quickstart
   deep
   api
   api_changelog
   contributing
