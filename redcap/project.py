#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User facing class for interacting with a REDCap Project"""

from typing import Optional

import semantic_version

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
    """Main class for interacting with REDCap projects"""

    @property
    def redcap_version(self) -> Optional[semantic_version.Version]:
        """REDCap version of the Project"""
        try:
            return self._redcap_version
        except AttributeError:
            self._redcap_version = self.export_version()
            return self._redcap_version

    def metadata_type(self, field_name):
        """If the given field_name is validated by REDCap, return it's type"""
        return self._meta_metadata(
            field_name, "text_validation_type_or_show_slider_number"
        )
