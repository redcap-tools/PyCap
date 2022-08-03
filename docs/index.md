# PyCap

PyCap is an interface to the [REDCap](http://www.project-redcap.org) Application Programming Interface (API). PyCap is designed to be a minimal interface exposing all required and optional API parameters. Our hope is that it makes simple things easy & hard things possible.

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

## Philosophy

The REDCap API is pretty simple. There is no built-in search or pagination, for example. However, it does expose all the functionality required to build advanced data management services on top of the API.

In the same way, PyCap is minimal by design. It doesn't do anything fancy behind the scenes and will not prevent you from shooting yourself in the foot. However, it should be very easy to understand and mentally-map PyCap functionality to the REDCap API.

## License

PyCap is licensed under the [MIT license](http://opensource.org/licenses/MIT).

## Citing

If you use PyCap in your research, please consider citing the software:

```
Burns, S. S., Browne, A., Davis, G. N., Rimrodt, S. L., & Cutting, L. E. PyCap (Version 1.0) [Computer Software].
Nashville, TN: Vanderbilt University and Philadelphia, PA: Childrens Hospital of Philadelphia.
Available from https://github.com/redcap-tools/PyCap. doi:10.5281/zenodo.9917
```
