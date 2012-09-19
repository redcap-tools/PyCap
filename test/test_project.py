#! /usr/bin/env python

import unittest

try:
    import pandas as pd
    skip_csv_tests = False
except ImportError:
    skip_csv_tests = True

from redcap import Project


class ProjectTests(unittest.TestCase):
    """docstring for ProjectTests"""

    def setUp(self):
        self.url = 'https://redcap.vanderbilt.edu/api/'
        self.long_proj = Project(self.url, '1387872621BBF1C17CC47FD8AE25FF54')
        self.reg_proj = Project(self.url, '8E66DB6844D58E990075AFB51658A002')

    def tearDown(self):
        pass

    def test_good_init(self):
        """Ensure basic instantiation """
        self.assertIsInstance(self.long_proj, Project)
        self.assertIsInstance(self.reg_proj, Project)

    def test_normal_attrs(self):
        """Ensure projects are created with all normal attrs"""
        for attr in ('metadata', 'field_names', 'field_labels', 'forms',
            'events', 'arm_names', 'arm_nums', 'def_field'):
            self.assertTrue(hasattr(self.reg_proj, attr))

    def test_long_attrs(self):
        """proj.events/arm_names/arm_nums should not be empty in long projects"""
        self.assertIsNotNone(self.long_proj.events)
        self.assertIsNotNone(self.long_proj.arm_names)
        self.assertIsNotNone(self.long_proj.arm_nums)

    def test_regular_attrs(self):
        """proj.events/arm_names/arm_nums should be empty tuples"""
        for attr in 'events', 'arm_names', 'arm_nums':
            attr_obj = getattr(self.reg_proj, attr)
            self.assertIsNotNone(attr_obj)
            self.assertEqual(len(attr_obj), 0)

    def test_obj_export(self):
        """ Make sure we get a list of dicts"""
        data = self.reg_proj.export_records()
        self.assertIsInstance(data, list)
        for record in data:
            self.assertIsInstance(record, dict)

    def test_long_export(self):
        """After determining a unique event name, make sure we get a
        list of dicts"""
        unique_event = self.long_proj.events[0]['unique_event_name']
        data = self.long_proj.export_records(events=[unique_event])
        self.assertIsInstance(data, list)
        for record in data:
            self.assertIsInstance(record, dict)

    @unittest.skipIf(skip_csv_tests, "pandas not installed, skipping csv tests")
    def test_csv_export(self):
        """Test valid csv export """
        from StringIO import StringIO
        csv_buf = StringIO(self.reg_proj.export_records(format='csv'))
        df = pd.read_csv(csv_buf, index_col=self.reg_proj.def_field)
        self.assertIsInstance(df, pd.DataFrame)
