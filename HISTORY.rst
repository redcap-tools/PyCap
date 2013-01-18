HISTORY
-------

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
