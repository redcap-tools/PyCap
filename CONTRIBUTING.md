# Issues & Contributing

If you have an issue with `PyCap` or the REDCap API, please raise an issue on the [issues page](https://github.com/redcap-tools/PyCap/issues). We'll do our best to help where we can.

PyCap follows the [Fork-Pull workflow](https://help.github.com/articles/using-pull-requests#fork--pull) method for accepting contributions. If you'd like to contribute code to `PyCap`, please use the following workflow:

1. If you don't already have an account on GitHub, please make one.
2. Fork [this repo](https://github.com/redcap-tools/PyCap) to your own account.
3. Checkout a branch & commit your changes. See the section on `poetry` below for instructions how to set up your local development environment. Tests are definitely appreciated :100:!
4. Push those changes to your repo & submit a Pull-Request to this repository.

If any of these steps are unclear, please peruse the helpful [GitHub Guide on Forking](https://guides.github.com/activities/forking/) or file an issue, and we'll try to help out!

## Using `poetry`

This package uses [`poetry`](https://python-poetry.org/docs/master/#installation) for dependency management and publishing. It is required in order to do local development with `PyCap`.

1. Install `poetry`

```sh
$ curl -sSL https://install.python-poetry.org | python3 -
```

2. Install all project dependencies (including development/optional dependencies).

```sh
$ poetry install -E data_science
```

3. Add your changes and make sure your changes pass all tests.

```
$ poetry run pytest
```

If you make changes to the dependencies you'll need to handle
them with the [`poetry add/remove`](https://python-poetry.org/docs/master/basic-usage/#installing-dependencies) commands.
