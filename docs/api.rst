API
===

PyCap is structured into two layers: a high level that exposes ``redcap.Project`` and a low-level, ``redcap.request``. Users (like yourself) should generally only worry about working the ``redcap.Project`` class.


High-Level
----------

The :class:`redcap.Project` class is the high-level object of the module. Generally you'll only need this class.

.. automodule:: redcap.project
    :members:
    :special-members: __init__

.. exception:: redcap.RedcapError

    This is thrown when an API method fails. Depending on the API call, the REDCap server will return a helpful message. Sometimes it won't :(

Low-Level
---------

The ``Project`` class makes all HTTP calls to the REDCap API through the :class:`redcap.request.RCRequest` class. You shouldn't need this in day-to-day usage.

.. automodule:: redcap.request
    :members:
    :special-members: __init__

