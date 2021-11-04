#! /usr/bin/env python
"""Test suite for Project class against mocked REDCap server"""
# pylint: disable=missing-function-docstring
from redcap import Project


def test_basic_init(simple_project):
    assert isinstance(simple_project, Project)


def test_simple_json_export(simple_project):
    data = simple_project.export_records()

    assert isinstance(data, list)
    for record in data:
        assert isinstance(record, dict)
