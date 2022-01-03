# Using PyCap in an app/package

If you're using PyCap for a small script/ad-hoc data pull, then the `Project` class has the all the necessary functionality. Similarly, the `Project` class is a good choice if you need access to a wide array of functionality (export records, surveys, user, etc.).

However, if you only are using one piece of the REDCap API, then you might want to consider using one of the more _focused_ and _simpler_ classes.

For example, if all you want to do is export/import records from your project, then `Records` class can meet all of your needs, with it's [`Records.export_records`](../api_reference/records/#redcap.methods.records.Records.export_records) and [`Records.import_records`](../api_reference/records/#redcap.methods.records.Records.import_records) methods.

In fact, these methods are exactly the same as the `Project.export_records` and `Project.import_records` methods. The `Project` class directly inherits them from the `Records` class.

The benefit of using the `Records` class over the `Project` class in this case for your application or package is getting to use a simpler class (easy for the developer) and only having to depend on a simpler class (better for the app).

For a full list of all `Project` subclasses, see the [API Reference](../api_reference/project).
