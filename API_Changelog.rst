API Change Log
==============

All changes to the REDCap API to be considered for addition into PyCap
are listed below by REDCap version number (oldest first).

The API Change Log assumes PyCap 1.0 is up-to-date as of REDCap 6.0.0, however all changes made from REDCap 6.X are included for sake of completeness.

New API methods, new parameters, and significant changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Note:** while some "significant changes" listed may not directly
influence PyCap methods and parameters, implementation procedures and/or
output may be effected such that they were listed as a precautionary
measure.

(6.0.0)
^^^^^^^

-  **Data Export rights - Significant changes** - New user rights
   privilege for Data Export rights: "Remove all tagged Identifier
   fields" - If a user is given this data export privilege setting, then
   it will be applied to \*all\* data export files in all modules where
   data is exported (e.g., PDFs, reports, API). In reports and in API
   data exports, any fields that have been tagged as Identifier fields
   will simply be removed from the export file. However, in PDF exports,
   it will include the Identifier fields in the PDF, but it will remove
   and replace any saved data values with the text *DATA REMOVED* for
   such fields.
-  **Export REDCap Version - New API method** - Returns the current
   REDCap version number as plain text (e.g., 4.13.18, 5.12.2, 6.0.0).
   Set the parameter content="version" in the API request, and it will
   return the REDCap version number.
-  **Export Reports - New API method** - Any report created by a user
   can be exported via the API in JSON, XML, or CSV format. Needed for
   the API request is the report ID number, which is listed next to the
   report name on the "Data Exports, Reports, and Stats" page (only
   displayed there if the user has API Export privileges). In order to
   export a report via the API, the user must have been given access to
   that report, must not have "No Access" data export rights, and must
   have API Export rights. More details regarding the API Export Reports
   method can be found on the API Documentation page.
-  **Export Records and Export Reports - New parameters** -
   "rawOrLabelHeaders" parameter for "Export Records" and "Export
   Reports" API methods. Possible values: "raw" (default) or "label".
   Parameter is valid for "csv" format only (and only works for "flat"
   type output). Allows one to have the API return the CSV headers in
   the data export either as the variable/field names
   (rawOrLabelHeaders=raw, or if rawOrLabelHeaders is not specified) or
   instead as the field labels (rawOrLabelHeaders=label).
-  **Export Records and Export Reports - New parameters** -
   "exportCheckboxLabels" parameter for "Export Records" and "Export
   Reports" API methods. Possible values: "true" or "false" (default).
   Parameter is only valid for "flat" type output. Allows one to set the
   format of checkbox field values when specifically exporting the data
   as labels (i.e., when rawOrLabel=true). When exporting labels, by
   default (without providing the exportCheckboxLabel flag or if
   exportCheckboxLabel=false), all checkboxes will either have a value
   "Checked" if they are checked or "Unchecked" if not checked. But if
   exportCheckboxLabel is set to true, it will instead export the
   checkbox value as the checkbox option's label (e.g., "Choice 1") if
   checked or it will be blank/empty (no value) if not checked.
-  **Export Records - Significant change** - For the "Export Records"
   API method when using "flat" type output while exporting the data as
   labels (i.e., when rawOrLabel=label), it now no longer defaults to
   exporting checkbox field values as their choice label (i.e., "Choice
   1") as it did in previous versions, but instead it returns "Checked"
   or "Unchecked" as the checkbox values by default. So if any users
   depend upon checkbox values being exported as their choice label,
   they should add the new parameter "exportCheckboxLabels" to their
   script as exportCheckboxLabels=true to maintain continuity after the
   upgrade to REDCap 6.0 or higher.
-  **Data Export user rights - Significant change** - Data Export user
   rights are now applied to API data exports. In previous versions, the
   data export rights had no effect on API data exports. Now if a user
   has No Access export rights, they will not be able to export data
   from the API (this includes the "Export Records" API method, the new
   "Export Reports" API method, and also the "Export a File" API
   method). And if the user has either "De-Identified" export rights or
   "Remove all tagged Identifier fields" export rights, then fields will
   be removed from the export data set accordingly in the API export
   request. If a user attempts to use the "Export a File" API method on
   a File Upload field that has been tagged as an Identifier when that
   user has either "De-Identified" export rights or "Remove all tagged
   Identifier fields" export rights, then it will return an error.
-  **Export Records - Significant change** - For the "Export Records"
   API method, "both" will no longer be an option for the "rawOrLabel"
   parameter. The only valid options for rawOrLabel will be "raw" and
   "label". This is also true for the new "Export Reports" API method.
-  **Data Exports - Significant change** - "eventName" will no longer be
   used as a parameter in API data exports. In previous versions, users
   could manually set whether an API data export would return the event
   name for longitudinal projects as the event label text or instead as
   the unique event name (generated automatically from the event label).
   It now simply returns the event label text if rawOrLabel=label,
   whereas it will return the unique event name if rawOrLabel=raw (or if
   rawOrLabel is not provided). If "eventName" is provided in the API
   request, it will be ignored.
-  **Data Exports - Significant change** - When doing an API data export
   where a list of fields or forms are explicitly provided in the API
   request to REDCap, the record ID field will now only be included in
   the exported result if the record ID field is explicitly specified in
   the list of fields or if its form is explicitly specified in the list
   of forms. In previous versions, if *any* form or field was explicitly
   provided in the API request, it would return the record ID field. So
   for users who depend upon the Record ID field to be returned in the
   exported data set, they should go ahead and add the Record ID to the
   "fields" array parameter in their API request to maintain continuity
   after the upgrade to REDCap 6.0 or higher.

(6.2.0)
^^^^^^^

-  **Signature fields - Significant change** - Allows a person to draw
   their signature on a survey or data entry form using a mouse, pen, or
   finger (depending on whether using a desktop computer or mobile
   device). Once captured, the signature will be displayed as an inline
   image on the survey page or data entry form. While this option
   appears as a "Signature" field type in the Online Designer, it is
   specified in the Data Dictionary as a "file" type field with
   validation type of "signature". Thus, it is essentially a special
   type of File Upload field. Note: The signature image for Signature
   fields cannot be imported via the API, although they can be
   downloaded or deleted via the API using the "Export a File" and
   "Delete a File" API methods, respectively.

(6.3.0)
^^^^^^^

-  **Server-side auto-calculations - Significant change** - When
   performing a data import (via Data Import Tool or API), REDCap will
   now perform the calculations for any calculated fields that are
   triggered by the values being imported. For example, if you have a
   BMI field whose calculation is based off of a height field and a
   weight field, then if you perform a data import of height and weight
   values, it will automatically calculate the BMI for each record that
   is imported and also save those calculations (and thus log them too
   on the Logging page). Auto-calculations are now also triggered when
   using cross-form calculations in the case where the calculated field
   exists on a different instrument than the fields being entered that
   are used in the calculation. So while in previous versions users
   would have to go to the instrument where the calculated field existed
   and would have to click Save to store the calculation, users now no
   longer have to do that because the calculation is performed and saved
   automatically at the time when the trigger fields are initially
   entered or changed. So essentially, users never have to worry that
   calculations are not being performed or saved in certain situations.
   They should expect that calculations are now always being saved
   silently in the background.

(6.4.0)
^^^^^^^

-  **Export PDF file of Data Collection Instruments - New API method** -
   Returns a PDF file of one or all instruments in the project, either
   with no data (blank), with a single record's data, or with all
   records from the project.
-  **Export a Survey Link for a Participant - New API method** - Returns
   a unique survey link (i.e., a URL) in plain text format for a
   specified record and data collection instrument (and event, if
   longitudinal) in a project.
-  **Export a Survey Queue Link for a Participant - New API method** -
   Returns a unique Survey Queue link (i.e., a URL) in plain text format
   for the specified record in a project that is utilizing the Survey
   Queue feature.
-  **Export a Survey Return Code for a Participant - New API method** -
   Returns a unique Return Code in plain text format for a specified
   record and data collection instrument (and event, if longitudinal) in
   a project with surveys that are utilizing the "Save & Return Later"
   feature.
-  **Export a Survey Participant List - New API method** - Returns the
   list of all participants for a specific survey instrument (and for a
   specific event, if a longitudinal project).
-  **Export List of Export Field Names - New API method** - Returns a
   list of the export/import-specific version of field names for all
   fields (or for one field, if desired) in a project. This is mostly
   used for checkbox fields because during data exports and data
   imports, checkbox fields have a different variable name used than the
   exact one defined for them in the Online Designer and Data
   Dictionary, in which \*each checkbox option\* gets represented as its
   own export field name in the following format: field\_name + triple
   underscore + converted coded value for the choice.
-  **All data import methods - Significant change** - Negative values
   can now be used as the raw coded values for checkbox fields with
   regard to their usage in data exports and data imports. In previous
   versions, negative values for checkbox choices would save
   successfully on surveys and data entry forms, but due to certain
   limitations, they would not work when importing values for those
   choices using the Data Import Tool or using the API data import. In
   the same regard, they would also cause problems when exporting data
   into a statistical analysis package. Now negative signs can be used
   for checkbox options, in which the negative sign will be replaced by
   an underscore in the export/import-specific version of the variable
   name (e.g., for a checkbox named "meds", its choices "2" and "-2"
   would export as the fields "meds\_2" and "meds2", respectively).

(6.4.3)
^^^^^^^

-  **Export PDF - Significant change** - The "Export PDF" API method's
   optional parameter "allrecords" has been changed to "!allRecords" to
   be more consistent with API parameter naming conventions. Note: To be
   backward compatible, the older version "allrecords" will still work
   the same as before if it is used.

(6.5.0)
^^^^^^^

-  **Export Project Information - New API method** - Exports some of the
   basic attributes of a given REDCap project, such as the project's
   title, if it is longitudinal, if surveys are enabled, the time the
   project was created and moved to production, etc. See the official
   API documention/help page in 6.5.0 for all the details.
-  **Export Users - Significant change** - "Export Users" will now
   return two new attributes for each user: "mobile\_app" and
   "mobile\_app\_download\_data". If mobile\_app's value is "1", then
   the user has privileges to use the REDCap Mobile App for that
   project. If "0", then not. If mobile\_app\_download\_data's value is
   "1", then the user has the ability to download all records from the
   project to the mobile app, but if "0", then the user will not have
   the option in the app to download any records to the app.

(6.7.0)
^^^^^^^

-  **Export Project Information - Significant Change** - Improvement:
   New project-level attributes are now included in the "Export Project
   Information" API method. The following attributes were added:
   "project\_irb\_number", "project\_grant\_number",
   "project\_pi\_firstname", and "project\_pi\_lastname".

(6.8.1)
^^^^^^^

-  **Server-side auto-calculations - Significant change** -
   Administrators may disable the auto-calculation functionality for a
   given project on the "Edit a Project's Settings" page in the Control
   Center. If left as enabled (default), server-side auto-calculations
   (introduced in REDCap 6.3.0) will be performed for calc fields when
   data is imported (via Data Import Tool or API) or when saving a
   form/survey containing cross-form or cross-event calculations. If
   auto-calculations are disabled, then calculations will only be done
   after being performed via JavaScript (client-side) on the data entry
   form or survey page on which they are located, and they will not be
   done on data imports. Tip: This setting should \*only\* be disabled
   if the auto-calculations are causing excessive slowdown when saving
   data. If disabled, then some calculations might not get performed,
   and if so, must then be fixed with Data Quality rule H.

(6.9.5)
^^^^^^^

-  **All API tokens - Signficant change** - The API is now more strict
   with regard to the validation of API tokens sent in API requests. In
   previous versions, if the token was longer than 32 characters, it
   would truncate the token to 32 characters (which is the expected
   length). It no longer truncates the token if longer than expected but
   merely returns an error message.

(6.10.0)
^^^^^^^^

-  **All data import methods - Significant change** - When importing
   data in CSV format via API or Data Import Tool, all blank rows will
   now be ignored instead of returning an error. This is to avoid the
   common mistake by users of leaving some lines as blank in the CSV
   file since most users assume the blank line would be ignored anyway.

(6.11.0)
^^^^^^^^

-  **Arm import/delete - New API method** - for longitudinal projects
   only; requires API Import privileges and Project privileges
-  **Event import/delete - New API method** - for longitudinal projects
   only; requires API Import privileges and Project privileges
-  **Import instrument-event mappings - New API method** - for
   longitudinal projects only; requires API Import privileges and
   Project privileges
-  **Import metadata, i.e. data dictionary - New API method** -
   available only in development status; requires API Import privileges
   and Project privileges
-  **Import users - New API method** - (import new users into a project
   while setting their user privileges, or update the privileges of
   existing users in the project.) - requires API Import privileges and
   User Rights privileges
-  **Create project - New API method**

   -  Allows a user to create a new REDCap project while setting some
      project attributes, such as project title, project purpose,
      enable/disable record auto-numbering, enable the project as
      longitudinal, and enable surveys in the project.
   -  This method requires a Super API Token that must be granted to a
      user by a REDCap administrator on the API Tokens page in the
      Control Center.
   -  After the super token has been granted, the user can view the
      super token on their My Profile page.

-  **Export Records - New parameter** - A new optional API parameter
   named "filterLogic" was API method "Export Records". filterLogic
   should be a string of logic text (e.g., age 30) for filtering the
   data to be returned by this API method, in which the API will only
   return the records (or record-events, if a longitudinal project)
   where the logic evaluates as TRUE. This parameter is blank/null by
   default unless a value is supplied. Please note that if the filter
   logic contains any incorrect syntax, the API will respond with an
   error message.
-  **Export Users - Significant change** - Change: For the API method
   "Export Users", many more user privilege rights are included in the
   response. The following is the full header list:

   -  username,email,firstname,lastname,expiration,data\_access\_group,data\_access\_group\_id,design,
      user\_rights,data\_access\_groups,data\_export,reports,stats\_and\_charts,manage\_survey\_participants,
      calendar,data\_import\_tool,data\_comparison\_tool,logging,file\_repository,data\_quality\_create,
      data\_quality\_execute,api\_export,api\_import,mobile\_app,mobile\_app\_download\_data,record\_create,
      record\_rename,record\_delete,lock\_records\_all\_forms,lock\_records,lock\_records\_customization,forms

-  **Export Users - Significant change** - Change: For the API method
   "Export Users", when requesting a response in CSV format, form-level
   rights are returned in a different format in order to prevent
   possible duplication of other new user privileges that are returned,
   in which all form rights will now be consolidated into a single
   column named "forms" (whereas in previous versions each form was
   represented as an individual column). The last column of the CSV
   string returned will have "forms" as the header, and the value will
   be each unique form name and its numerical value as a colon-separated
   pair with all the form value pairs strung together as a single
   comma-separated string (e.g.
   "demographics:1,visit\_data:3,baseline:1"). See a full CSV example
   below of two users exported from a project.

   -  username,email,firstname,lastname,expiration,data\_access\_group,data\_access\_group\_id,design,
      user\_rights,data\_access\_groups,data\_export,reports,stats\_and\_charts,manage\_survey\_participants,
      calendar,data\_import\_tool,data\_comparison\_tool,logging,file\_repository,data\_quality\_create,
      data\_quality\_execute,api\_export,api\_import,mobile\_app,mobile\_app\_download\_data,record\_create,
      record\_rename,record\_delete,lock\_records\_all\_forms,lock\_records,lock\_records\_customization,forms
      harrispa,baseline\_data:1,visit\_lab\_data:1,patient\_morale\_questionnaire:1,visit\_blood\_workup:1,
      completion\_data:1,completion\_project\_questionnaire:1,visit\_observed\_behavior:,baseline\_data:1,
      visit\_lab\_data:1,patient\_morale\_questionnaire:1,visit\_blood\_workup:1,completion\_data:1,
      completion\_project\_questionnaire:1,visit\_observed\_behavior:

-  **Export Users - Significant change** - Change: For the API method
   "Export Users", when requesting a response in XML format, the main
   parent tags at the beginning and end of the response will no longer
   be <records> but instead will be <users> to be less confusing (since
   "records" often denotes something else in REDCap) and also to be more
   consistent with how other API methods return XML items.
-  **Export Users - Significant change** - Change: For the API method
   "Export Users", the new "data\_access\_group\_id" field was added, in
   which it returns the numerical group ID number that the
   "data\_access\_group" field used to return in previous versions. And
   now, the unique group name of a user's Data Access Group is returned
   for the "data\_access\_group" field rather than the numerical group
   ID number.
-  **Export Instrument-Event Mappings - Significant change** - Change:
   The API method "Export Instrument-Event Mappings" now returns a
   different structure if exporting as JSON or XML (however, the CSV
   format will remain the same). It will now export with "arm\_num",
   "unique\_event\_name", and "form" as attributes of each item/mapping,
   as seen in the JSON/XML examples below.
-  **Export Project Information - Signficant change** - For "Export
   Project Information" API method, the following two project attributes
   were added:

   -  secondary\_unique\_field - The variable name of the secondary
      unique field defined in the project (if applicable).
   -  display\_today\_now\_button - Value will be "0" or "1" (i.e. False
      or True). If "0", then do NOT display the today/now button next to
      date/datetime fields on data entry forms and surveys. If "1"
      (default), display them.

(6.12.0)
^^^^^^^^

-  **Export Project XML - New API method** - Returns the contents of an
   entire project (records, events, arms, instruments, fields, and
   project attributes - even uploaded files and Descriptive field
   attachments) as a single XML file, which is in CDISC ODM format.
-  **Import Records - New parameter** - for data format now accepts
   value of "odm" to import data in CDISC ODM format. This only returns
   data (not the project structure/metadata).
-  **Create Project - New parameter** - named "odm" can be used to pass
   the ODM XML string of an entire project's structure (the same as
   output by the Export Project XML method) when creating a new project
   using a Super API Token. This will allow you not only to create the
   project with the API request, but also to import all fields, forms,
   and project attributes (and events and arms, if longitudinal) as well
   as record data all at the same time.
-  **Export Records - New Parameter** - Parameter for data format now
   accepts value of "odm" to export data in CDISC ODM format. This only
   returns data (not the project structure/metadata).

(6.12.1)
^^^^^^^^

-  **Export Project XML - New parameter** - exportFiles (boolean)
   parameter was added to the API method. The parameter, which defaults
   to FALSE, specifies whether or not the resulting XML will include all
   files (base64 encoded) that were uploaded for File Upload and
   Signature fields for all records in the project. Please note that
   while the previous version (6.12.0) exported all files in the
   resulting XML by default, it no longer does that and must now be
   specified explicitly.
