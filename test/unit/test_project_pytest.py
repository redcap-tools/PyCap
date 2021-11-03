#! /usr/bin/env python
"""Test suite for Project class against mocked REDCap server"""
# pylint: disable=missing-function-docstring
from redcap import Project


def test_basic_init(normal_project):
    assert isinstance(normal_project, Project)


def test_normal_json_export(normal_project):
    data = normal_project.export_records()

    assert isinstance(data, list)
    for record in data:
        assert isinstance(record, dict)
