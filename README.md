# PyCap

[![CI](https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml/badge.svg)](https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/redcap-tools/PyCap/branch/master/graph/badge.svg?token=IRgcPzANxU)](https://codecov.io/gh/redcap-tools/PyCap)
[![PyPI](https://badge.fury.io/py/PyCap.svg)](https://badge.fury.io/py/PyCap)
[![black](https://img.shields.io/badge/code%20style-black-black)](https://pypi.org/project/black/)

## Intro

`PyCap` is a python module exposing the REDCap API through some helpful abstractions. Information about the REDCap project can be found at http://project-redcap.org/.

Available under the MIT license.

## Installation

Install the latest version with [`pip`](https://pypi.python.org/pypi/pip)

```sh
$ pip install PyCap
```

If you want to load REDCap data into [`pandas`](https://pandas.pydata.org/) dataframes, this will make sure you have `pandas` installed

```sh
$ pip install PyCap[pandas]
```

To install the bleeding edge version from the github repo, use the following

```sh
$ pip install -e git+https://github.com/redcap-tools/PyCap.git#egg=PyCap
```

## Documentation

Canonical documentation and usage examples can be found [here](http://redcap-tools.github.io/PyCap/).

## Features

Currently, these API calls are available:

### Export

* Field names
* Instrument-event mapping
* File
* Metadata
* Project Info
* Records
* Report
* Survey participant list
* Users
* Version

### Import

* File
* Metadata
* Records

### Delete

* File
* Records

### Other

* Generate next record name

## Citing

If you use PyCap in your research, please consider citing the software:

>    Burns, S. S., Browne, A., Davis, G. N., Rimrodt, S. L., & Cutting, L. E. PyCap (Version 1.0) [Computer Software].
>    Nashville, TN: Vanderbilt University and Philadelphia, PA: Childrens Hospital of Philadelphia.
>    Available from https://github.com/redcap-tools/PyCap. doi:10.5281/zenodo.9917
