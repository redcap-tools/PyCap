#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module exposes the REDCap API through the Project class. Instantiate the
class with the URL to your REDCap system along with an API key, probably
generated for you by a REDCap administrator.

With a Project object, you can view the metadata and export/import data.

Other API requests are available, such as exporting users & Form-Event Mappings.

"""

from redcap.project import Project
from redcap.request import _RCRequest, RedcapError

__author__ = "Scott Burns <scott.s.burns@gmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"
