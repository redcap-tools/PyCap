#! /usr/bin/env python

import unittest
from redcap import Project

try:
    import pandas as pd
    skip_pd = False
except ImportError:
    skip_pd = True


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
        "proj.events/arm_names/arm_nums should not be empty in long projects"
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

    def is_good_csv(self, csv_string):
        "Helper to test csv strings"
        return isinstance(csv_string, basestring)

    def test_csv_export(self):
        """Test valid csv export """
        csv = self.reg_proj.export_records(format='csv')
        self.assertTrue(self.is_good_csv(csv))

    def test_metadata_export(self):
        """Test valid metadata csv export"""
        csv = self.reg_proj.export_metadata(format='csv')
        self.assertTrue(self.is_good_csv(csv))

    def test_file_export(self):
        """Test file export and proper content-type parsing"""
        content, headers = self.reg_proj.export_file(record='1', field='file')
        self.assertIsInstance(content, basestring)
        # We should at least get the filename in the headers
        for key in ['name']:
            self.assertIn(key, headers)

    def test_file_import(self):
        "Test file import"
        import os
        this_dir, this_fname = os.path.split(__file__)
        upload_fname = os.path.join(this_dir, 'data.txt')
        # Test a well-formed request
        with open(upload_fname, 'r') as fobj:
            response = self.reg_proj.import_file('1', 'file', upload_fname, fobj)
        self.assertTrue('error' not in response)
        # Test importing a file to a non-file field raises a ValueError
        with open(upload_fname, 'r') as fobj:
            with self.assertRaises(ValueError):
                response = self.reg_proj.import_file('1', 'first_name',
                    upload_fname, fobj)

    @unittest.skipIf(skip_pd, "Couldnl't import pandas")
    def test_metadata_to_df(self):
        """Test metadata export --> DataFrame"""
        df = self.reg_proj.export_metadata(format='df')
        self.assertIsInstance(df, pd.DataFrame)

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    def test_export_to_df(self):
        """Test export --> DataFrame"""
        df = self.reg_proj.export_records(format='df')
        self.assertIsInstance(df, pd.DataFrame)

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    def test_export_df_kwargs(self):
        """Test passing kwargs to export DataFrame construction"""
        df = self.reg_proj.export_records(format='df',
            df_kwargs={'index_col': 'first_name'})
        self.assertEqual(df.index.name, 'first_name')
        self.assertTrue('study_id' in df)

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    def test_metadata_df_kwargs(self):
        """Test passing kwargs to metadata DataFrame construction"""
        df = self.reg_proj.export_metadata(format='df',
            df_kwargs={'index_col': 'field_label'})
        self.assertEqual(df.index.name, 'field_label')
        self.assertTrue('field_name' in df)
