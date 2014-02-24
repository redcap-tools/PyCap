Introduction
============

PyCap is designed to be a minimal interface between you and the REDCap Application Programming Interface (API). All required and optional parameters for the API should be exposed through PyCap and it should extremely easy to discern their mapping.

Philosophy
----------

The REDCap API is pretty minimal. There is no built-in search or pagination, for example. However, it does expose all the functionality required to build advanced data management services on top of the API.

In the same way, PyCap is minimal by design. It doesn't do anything fancy behind the scenes and will not prevent you from shooting yourself in the foot. However, it should be very easy to understand and mentally-map PyCap functionality to the REDCap API.

License
-------

PyCap is licensed under the `MIT license <http://opensource.org/licenses/MIT>`_.