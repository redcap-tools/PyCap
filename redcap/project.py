#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User facing class for interacting with a REDCap Project"""

from typing import Optional

import semantic_version  # type: ignore

from redcap import methods

__author__ = "Scott Burns <scott.s.burnsgmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"

# We're designing this class to be lazy by default, and not hit the API unless
# explicitly requested by the user. We also want to keep the methods separated,
# which means multi-layered inheritance is our best bet.
# pylint: disable=attribute-defined-outside-init,too-many-ancestors


class Project(
    methods.field_names.FieldNames,
    methods.files.Files,
    methods.instruments.Instruments,
    methods.metadata.Metadata,
    methods.project_info.ProjectInfo,
    methods.records.Records,
    methods.reports.Reports,
    methods.surveys.Surveys,
    methods.users.Users,
    methods.version.Version,
):
    """Main class for interacting with REDCap projects

    Attributes:
        verify_ssl: Verify SSL, default True. Can pass path to CA_BUNDLE

    Note:
        Your REDCap token should be kept **secret**! Treat it like a password
        and NEVER save it directly in your script/application. Rather it should be obscured
        and retrieved 'behind the scenes'. For example, saving the token as an environment
        variable and retrieving it with `os.getenv`. The creation of the `TOKEN` string in
        the example is not shown, for the above reasons

    Examples:
        >>> from redcap import Project
        >>> URL = "https://redcapdemo.vanderbilt.edu/api/"
        >>> proj = Project(URL, TOKEN)
        >>> proj.field_names
        ['record_id', 'field_1', 'checkbox_field', 'upload_field']
        >>> proj.is_longitudinal
        True
        >>> proj.def_field
        'record_id'

        The url and token attributes are read-only, to prevent users from accidentally
        overwriting them
        >>> proj.url = "whoops"
        Traceback (most recent call last):
        ...
        AttributeError: ...
    """

    @property
    def redcap_version(self) -> Optional[semantic_version.Version]:
        """REDCap version of the Project"""
        self._redcap_version: Optional[semantic_version.Version]
        try:
            return self._redcap_version
        except AttributeError:
            self._redcap_version = self.export_version()
            return self._redcap_version
