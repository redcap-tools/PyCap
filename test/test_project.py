#! /usr/bin/env python

import unittest
from redcap import Project, RedcapError
import semantic_version

skip_pd = False
try:
    import pandas as pd
except ImportError:
    skip_pd = True


class ProjectTests(unittest.TestCase):
    """docstring for ProjectTests"""

    url = 'https://redcap.vanderbilt.edu/api/'
    bad_url = 'https://redcap.vanderbilt.edu/api'
    reg_token = '8E66DB6844D58E990075AFB51658A002'
    long_proj = Project(url, '1387872621BBF1C17CC47FD8AE25FF54')
    reg_proj = Project(url, reg_token)
    ssl_proj = Project(url, reg_token, verify_ssl=False)
    survey_proj = Project(url, '37CAB1ABC2FEB3BB9D821DF13BA38A7B')

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_good_init(self):
        """Ensure basic instantiation """
        self.assertIsInstance(self.long_proj, Project)
        self.assertIsInstance(self.reg_proj, Project)
        self.assertIsInstance(self.ssl_proj, Project)

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

    def test_is_longitudinal(self):
        "Test the is_longitudinal method"
        self.assertFalse(self.reg_proj.is_longitudinal())
        self.assertTrue(self.long_proj.is_longitudinal())

    def test_regular_attrs(self):
        """proj.events/arm_names/arm_nums should be empty tuples"""
        for attr in 'events', 'arm_names', 'arm_nums':
            attr_obj = getattr(self.reg_proj, attr)
            self.assertIsNotNone(attr_obj)
            self.assertEqual(len(attr_obj), 0)

    def test_json_export(self):
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

    def test_import_records(self):
        "Test record import"
        data = self.reg_proj.export_records()
        response = self.reg_proj.import_records(data)
        self.assertIn('count', response)
        self.assertNotIn('error', response)

    def test_import_exception(self):
        "Test record import throws RedcapError for bad import"
        data = self.reg_proj.export_records()
        data[0]['non_existent_key'] = 'foo'
        with self.assertRaises(RedcapError) as cm:
            self.reg_proj.import_records(data)
        exc = cm.exception
        self.assertIn('error', exc.args[0])

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

    def test_bad_creds(self):
        "Test that exceptions are raised with bad URL or tokens"
        with self.assertRaises(RedcapError):
            Project(self.bad_url, self.reg_token)
        with self.assertRaises(RedcapError):
            Project(self.url, '1')

    def test_fem_export(self):
        """ Test fem export in json format gives list of dicts"""
        fem = self.long_proj.export_fem(format='json')
        self.assertIsInstance(fem, list)
        for arm in fem:
            self.assertIsInstance(arm, dict)

    def test_file_export(self):
        """Test file export and proper content-type parsing"""
        record, field = '1', 'file'
        #Upload first to make sure file is there
        self.import_file()
        # Now export it
        content, headers = self.reg_proj.export_file(record, field)
        self.assertIsInstance(content, basestring)
        # We should at least get the filename in the headers
        for key in ['name']:
            self.assertIn(key, headers)
        # needs to raise ValueError for exporting non-file fields
        with self.assertRaises(ValueError):
            self.reg_proj.export_file(record=record, field='dob')
        # Delete and make sure we get an RedcapError with next export
        self.reg_proj.delete_file(record, field)
        with self.assertRaises(RedcapError):
            self.reg_proj.export_file(record, field)

    def import_file(self):
        upload_fname = self.upload_fname()
        with open(upload_fname, 'r') as fobj:
            response = self.reg_proj.import_file('1', 'file', upload_fname, fobj)
        return response

    def upload_fname(self):
        import os
        this_dir, this_fname = os.path.split(__file__)
        return os.path.join(this_dir, 'data.txt')

    def test_file_import(self):
        "Test file import"
        # Make sure a well-formed request doesn't throw RedcapError
        try:
            response = self.import_file()
        except RedcapError:
            self.fail("Shouldn't throw RedcapError for successful imports")
        self.assertTrue('error' not in response)
        # Test importing a file to a non-file field raises a ValueError
        fname = self.upload_fname()
        with open(fname, 'r') as fobj:
            with self.assertRaises(ValueError):
                response = self.reg_proj.import_file('1', 'first_name',
                    fname, fobj)

    def test_file_delete(self):
        "Test file deletion"
        # upload a file
        fname = self.upload_fname()
        with open(fname, 'r') as fobj:
            self.reg_proj.import_file('1', 'file', fname, fobj)
        # make sure deleting doesn't raise
        try:
            self.reg_proj.delete_file('1', 'file')
        except RedcapError:
            self.fail("Shouldn't throw RedcapError for successful deletes")

    def test_user_export(self):
        "Test user export"
        users = self.reg_proj.export_users()
        # A project must have at least one user
        self.assertTrue(len(users) > 0)
        req_keys = ['firstname', 'lastname', 'email', 'username',
                    'expiration', 'data_access_group', 'data_export',
                    'forms']
        for user in users:
            for key in req_keys:
                self.assertIn(key, user)

    def test_verify_ssl(self):
        """Test argument making for SSL verification"""
        # Test we won't verify SSL cert for non-verified project
        post_kwargs = self.ssl_proj._kwargs()
        self.assertIn('verify', post_kwargs)
        self.assertFalse(post_kwargs['verify'])
        # Test we do verify SSL cert in normal project
        post_kwargs = self.reg_proj._kwargs()
        self.assertIn('verify', post_kwargs)
        self.assertTrue(post_kwargs['verify'])

    def test_export_data_access_groups(self):
        """Test we get 'redcap_data_access_group' in exported data"""
        records = self.reg_proj.export_records(export_data_access_groups=True)
        for record in records:
            self.assertIn('redcap_data_access_group', record)
        # When not passed, that key shouldn't be there
        records = self.reg_proj.export_records()
        for record in records:
            self.assertNotIn('redcap_data_access_group', record)

    def test_export_survey_fields(self):
        """Test that we get the appropriate survey keys in the exported
        data.

        Note that the 'demographics' form has been setup as the survey
        in the `survey_proj` project. The _timestamp field will vary for
        users as their survey form will be named differently"""
        records = self.survey_proj.export_records(export_survey_fields=True)
        for record in records:
            self.assertIn('redcap_survey_identifier', record)
            self.assertIn('demographics_timestamp', record)
        # The regular project doesn't have a survey setup. Users should
        # be able this argument as True but it winds up a no-op.
        records = self.reg_proj.export_records(export_survey_fields=True)
        for record in records:
            self.assertNotIn('redcap_survey_identifier', record)
            self.assertNotIn('demographics_timestamp', record)

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    def test_metadata_to_df(self):
        """Test metadata export --> DataFrame"""
        df = self.reg_proj.export_metadata(format='df')
        self.assertIsInstance(df, pd.DataFrame)

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    def test_export_to_df(self):
        """Test export --> DataFrame"""
        df = self.reg_proj.export_records(format='df')
        self.assertIsInstance(df, pd.DataFrame)
        # Test it's a normal index
        self.assertTrue(hasattr(df.index, 'name'))
        # Test for a MultiIndex on longitudinal df
        long_df = self.long_proj.export_records(format='df', event_name='raw')
        self.assertTrue(hasattr(long_df.index, 'names'))

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

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    def test_import_dataframe(self):
        """Test importing a pandas.DataFrame"""
        df = self.reg_proj.export_records(format='df')
        # grrr coerce implicilty converted floats to str(int())
        for col in ['matrix1', 'matrix2', 'matrix3', 'sex']:
            df[col] = map(lambda x: str(int(x)) if pd.notnull(x) else '', df[col])
        response = self.reg_proj.import_records(df)
        self.assertIn('count', response)
        self.assertNotIn('error', response)
        long_df = self.long_proj.export_records(event_name='raw', format='df')
        response = self.long_proj.import_records(long_df)
        self.assertIn('count', response)
        self.assertNotIn('error', response)

    def test_date_formatting(self):
        """Test date_format parameter"""

        def import_factory(date_string):
            return [{'study_id': '1',
                     'dob': date_string}]

        # Default YMD with dashes
        import_ymd = import_factory('2000-01-01')
        response = self.reg_proj.import_records(import_ymd)
        self.assertEqual(response['count'], 1)

        # DMY with /
        import_dmy = import_factory('31/01/2000')
        response = self.reg_proj.import_records(import_dmy, date_format='DMY')
        self.assertEqual(response['count'], 1)

        import_mdy = import_factory('12/31/2000')
        response = self.reg_proj.import_records(import_mdy, date_format='MDY')
        self.assertEqual(response['count'], 1)

    def test_get_version(self):
        """Testing retrieval of REDCap version associated with Project"""
        self.assertTrue(isinstance(semantic_version.Version('1.0.0'), type(self.long_proj.redcap_version)))

    def test_export_checkbox_labels(self):
        """Testing the export of checkbox labels as field values"""
        self.assertEqual(
            self.reg_proj.export_records(
                raw_or_label='label',
                export_checkbox_labels=True)[0]['matcheck1___1'],
                'Foo'
        )

    def test_export_always_include_def_field(self):
        """ Ensure def_field always comes in the output even if not explicity
        given in a requested form """
        # If we just ask for a form, must also get def_field in there
        records = self.reg_proj.export_records(forms=['imaging'])
        for record in records:
            self.assertIn(self.reg_proj.def_field, record)
        # , still need it def_field even if not asked for in form and fields
        records = self.reg_proj.export_records(forms=['imaging'], fields=['foo_score'])
        for record in records:
            self.assertIn(self.reg_proj.def_field, record)
        # If we just ask for some fields, still need def_field
        records = self.reg_proj.export_records(fields=['foo_score'])
        for record in records:
            self.assertIn(self.reg_proj.def_field, record)
