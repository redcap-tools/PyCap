#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Scott Burns <scott.s.burns@vanderbilt.edu>'
__license__ = 'MIT'
__copyright__ = '2014, Vanderbilt University'

"""
This module exposes the REDCap API through the Project class. Instantiate the
class with the URL to your REDCap system along with an API key, probably
generated for you by a REDCap administrator.

With a Project object, you can view the metadata and export/import data. You
can also build search queries with the Query/QueryGroup classes and use those
in conjunction with your Project to filter your data.

"""

from .project import Project
import warnings
warnings.warn("Query & QueryGroup will be removed at 1.0.", DeprecationWarning)
from .query import Query, QueryGroup
from .request import RCRequest, RCAPIError, RedcapError
from .version import VERSION as __version__
