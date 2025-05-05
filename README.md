# PyCap

[![CI](https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml/badge.svg)](https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/redcap-tools/PyCap/branch/master/graph/badge.svg?token=IRgcPzANxU)](https://codecov.io/gh/redcap-tools/PyCap)
[![PyPI version](https://badge.fury.io/py/pycap.svg)](https://badge.fury.io/py/pycap)
[![black](https://img.shields.io/badge/code%20style-black-black)](https://pypi.org/project/black/)

## Intro

`PyCap` is a python module exposing the REDCap API through some helpful abstractions. Information about the REDCap project can be found at https://project-redcap.org/.

Available under the MIT license.

## Installation

Install the latest version with [`pip`](https://pypi.python.org/pypi/pip)

```sh
$ pip install PyCap
```

If you want to load REDCap data into [`pandas`](https://pandas.pydata.org/) dataframes, this will make sure you have `pandas` installed

```sh
$ pip install PyCap[all]
```

To install the bleeding edge version from the github repo, use the following

```sh
$ pip install -e git+https://github.com/redcap-tools/PyCap.git#egg=PyCap
```

## Documentation

Canonical documentation and usage examples can be found [here](https://redcap-tools.github.io/PyCap/).

## Features

Currently, these API calls are available:

### Export

* Arms
* Data Access Groups
* Events
* Field names
* Instruments
* Instrument-event mapping
* File
* File Repository
* Logging
* Metadata
* Project Info
* PDF of instruments
* Records
* Repeating instruments and events
* Report
* Surveys
* Users
* User-DAG assignment
* User Roles
* User-Role assignment
* Version

### Import

* Arms
* Data Access Groups
* Events
* File
* File Repository
* Instrument-event mapping
* Metadata
* Records
* Repeating instruments and events
* Users
* User-DAG assignment
* User Roles
* User-Role assignment

### Delete

* Arms
* Data Access Groups
* Events
* File
* File Repository
* Records
* Users
* User Roles

### Other

* Generate next record name
* Switch data access group

## Citing

If you use PyCap in your research, please consider citing the software:

>    Burns, S. S., Browne, A., Davis, G. N., Rimrodt, S. L., & Cutting, L. E. PyCap (Version 1.0) [Computer Software].
>    Nashville, TN: Vanderbilt University and Philadelphia, PA: Childrens Hospital of Philadelphia.
>    Available from https://github.com/redcap-tools/PyCap. doi:10.5281/zenodo.9917
