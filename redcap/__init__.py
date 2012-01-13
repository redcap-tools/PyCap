#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module exposes the REDCap API through the Project class. Instantiate the
class with the URL to your REDCap system along with an API key, probably
generated for you by a REDCap administrator.

With a Project object, you can view the metadata and export/import data. You
can also build search queries with the Query/QueryGroup classes and use those
in conjunction with your Project to filter your data.

"""
__version__ = '0.3.4'

from .project import Project
from .query import Query, QueryGroup
from .request import RCRequest, RCAPIError
