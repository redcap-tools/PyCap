#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User facing class for interacting with a REDCap Project"""

from redcap import methods

__author__ = "Scott Burns <scott.s.burnsgmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"


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
):
    """Main class for interacting with REDCap projects"""

    def metadata_type(self, field_name):
        """If the given field_name is validated by REDCap, return it's type"""
        return self._meta_metadata(
            field_name, "text_validation_type_or_show_slider_number"
        )
