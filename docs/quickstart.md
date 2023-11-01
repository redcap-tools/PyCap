# Quickstart

PyCap makes it very simple to interact with the data stored in your REDCap projects

```python
from redcap import Project

api_url = 'https://redcap.example.edu/api/'
api_key = 'SomeSuperSecretAPIKeyThatNobodyElseShouldHave'
project = Project(api_url, api_key)
```

Export all the data

```python
data = project.export_records()
```

Import all the data

```python
to_import = [{'record': 'foo', 'test_score': 'bar'}]
response = project.import_records(to_import)
```

Import a file

```python
fname = 'something_to_upload.txt'
with open(fname, 'r') as fobj:
    project.import_file('1', 'file', fname, fobj)
```

Export a file

```python
content, headers = project.export_file('1', 'file')
with open(headers['name'], 'wb') as fobj:
    fobj.write(content)
```

Delete a file
```python
try:
    project.delete_file('1', 'file')
except redcap.RedcapError:
    # Throws this if file wasn't successfully deleted
    pass
except ValueError:
    # You screwed up and gave it a bad field name, etc
    pass
```

Export a PDF file of all instruments (blank)

```python
content, _headers = project.export_pdf()
with open('all_instruments_blank.pdf', 'wb') as fobj:
    fobj.write(content)
```
