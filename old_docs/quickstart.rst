Quickstart
==========

PyCap makes it very simple to interact with the data stored in your REDCap projects::

    from redcap import Project
    api_url = 'https://redcap.example.edu/api/'
    api_key = 'SomeSuperSecretAPIKeyThatNobodyElseShouldHave'
    project = Project(api_url, api_key)

Export all the data::

    data = project.export_records()

Import all the data::

    to_import = [{'record': 'foo', 'test_score': 'bar'}]
    response = project.import_records(to_import)

Import a file::

    fname = 'something_to_upload.txt'
    with open(fname, 'r') as fobj:
        project.import_file('1', 'file', fname, fobj)

Export a file::

    content, headers = project.export_file('1', 'file')
    with open(headers['name'], 'w') as fobj:
        fobj.write(content)

Delete a file::

    try:
        project.delete_file('1', 'file')
    except redcap.RedcapError:
        # Throws this if file wasn't successfully deleted
        pass
    except ValueError:
        # You screwed up and gave it a bad field name, etc
        pass

The deep-dive into all the methods can be found in the full :doc:`deep`.