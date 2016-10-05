HISTORY
-------

1.0.2 (2016-10-05)
+++++++++++++++++

* Fix issue in new survey participant export method.

1.0.1 (2016-10-05)
+++++++++++++++++

* Add a ``Project`` method to export the survey participant list.
* Update author email.

1.0 (2014-05-16)
++++++++++++++++

* Normalize all ``format`` argument to default to ``json``, not ``obj``. This better follows the official REDCap API. This breaks backwards compatibility, hence the 1.0 release.
* Remove the ``redcap.query`` and associated tests. If you need filtering functionality, `Pandas <http://pandas.pydata.org>`_ is **highly** recommended.
* Update documentation re: how PyCap implicitly decodes JSON responses.

0.9 (2014-02-27)
++++++++++++++++

* Update docs about passing CA_BUNDLE through ``verify_ssl``.
* Canonical URL for docs is now `http://pycap.rtfd.org <http://pycap.rtfd.org>`_.
* Add ``date_format`` argument for ``.import_records``
* Sphinxification of docs
* Add MIT license
* Add ``export_survey_fields`` & ``export_data_access_groups`` arguments for
  ``.import_records``
* Raise for 5XX responses
* Raise exception for failed imports
* Deprecate the entire ``redcap.Query`` module. It was a bad idea to begin with.
* Raise exception during ``Project`` instantiation when the metadata call fails.
  This is usually indicative of bad credentials.

0.8.1 (2013-05-16)
++++++++++++++++++

* By default, in longitudinal projects when exporting records as a data frame, the index will be a MultiIndex of the project's primary field and ``redcap_event_name``.
* DataFrames can be passed to ``Project.import_records``.
* Added ``Project.export_fem`` to export Form-Event Mappings from the Project.
* The SSL certificate on REDCap server can be ignored if need be.

0.8.0 (2013-02-14)
++++++++++++++++++

* Added rest of API methods: Project.export_users, Project.delete_file. Almost
    all API methods are implemented within ``Project`` in some way, shape or form.
* Fix file import bug.
* Now use relaxed JSON decoding because REDCap doesn't always send strict JSON.
* File export, import and delete methods will raise ``redcap.RedcapError`` when the
    methods don't succeed on the server.
* Low-level content handling has been cleaned up.


0.7.0 (2013-01-18)
++++++++++++++++++

* Added Project.export_file and Project.import_file methods for exporting/
  importing files from/to REDCap databases
* Fixed a dependency issue that would cause new installations to fail
* Fixed an issue where newline characters in the project's Data
  Dictionary would case Projects to fail instantiation.

0.6.1 (2012-11-16)
++++++++++++++++++

* Add ability to alter DataFrame construction with the 'df_kwargs' arg
  in Project.export_records and .export_metadata


0.6 (2012-11-06)
++++++++++++++++

* Add export_metadata function on redcap.Project class
* Add 'df' as an option for the format argument on the redcap.Project
    export methods to return a pandas.DataFrame

0.5.2 (2012-10-12)
++++++++++++++++++

* Update setup.py for more graceful building

0.5.1 (2012-10-04)
++++++++++++++++++

* Fix potential issue when exporting strange characters

0.5 (2012-09-19)
++++++++++++++++

* Add initial support for longitudinal databases
* Add helper attributes on redcap.Project class
* Improve testing
* Add Travis-CI testing on github

0.4.2 (2012-03-15)
++++++++++++++++++

* 0.4.1 didn't play well with pypi?

0.4.1 (2012-03-15)
++++++++++++++++++

* Defend against non-unicode characters in Redcap Project

0.3.4 (2012-01-12)
++++++++++++++++++

* New documentation

0.3.3 (2011-11-21)
++++++++++++++++++

* Bug fix when exporting all fields

0.3.2 (2011-11-21)
++++++++++++++++++

* Works with current version of requests
* Under-the-hood changes (only json is used for RCRequest)
* Bug fix in Project.filter

0.3.1 (2011-11-02)
++++++++++++++++++

* Bug fix in import_records


0.3 (2011-09-27)
++++++++++++++++

* Using Kenneth Reitz's request module, greatly simplifying request code.

0.21 (2011-09-14)
+++++++++++++++++

* First public release on PyPI
* Version bump

0.1 (2011-09-14)
+++++++++++++++++

* Basic import, export, metadata
