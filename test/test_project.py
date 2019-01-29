#! /usr/bin/env python

import unittest
import responses
import json
from redcap import Project, RedcapError
import semantic_version

skip_pd = False
try:
    import pandas as pd
except ImportError:
    skip_pd = True

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    basestring
except NameError:
    basestring = str


class ProjectTests(unittest.TestCase):
    """docstring for ProjectTests"""

    long_proj_url = 'https://redcap.longproject.edu/api/'
    normal_proj_url = 'https://redcap.normalproject.edu/api/'
    ssl_proj_url = 'https://redcap.sslproject.edu/api/'
    survey_proj_url = 'https://redcap.surveyproject.edu/api/'
    bad_url = 'https://redcap.badproject.edu/api'
    reg_token = 'supersecrettoken'

    def setUp(self):
        self.create_projects()

    def tearDown(self):
        pass

    def add_long_project_response(self):
        def request_callback_long(request):
            parsed = urlparse.urlparse("?{}".format(request.body))
            data = urlparse.parse_qs(parsed.query)
            headers = {"Content-Type": "application/json"}

            request_type = data["content"][0]

            if "returnContent" in data:
                resp = {"count": 1}

            elif (request_type == "metadata"):
                resp = [{
                    'field_name': 'record_id',
                    'field_label': 'Record ID',
                    'form_name': 'Test Form',
                    "arm_num": 1,
                    "name": "test"
                }]
            elif (request_type == "version"):
                resp = b'8.6.0'
                headers = {'content-type': 'text/csv; charset=utf-8'}
                return (201, headers, resp)
            elif (request_type == "event"):
                resp = [{
                    'unique_event_name': "raw"
                }]
            elif (request_type == "arm"):
                resp = [{
                    "arm_num": 1,
                    "name": "test"
                }]
            elif (request_type in ["record", "formEventMapping"]):
                if "csv" in data["format"]:
                    resp = "record_id,test,redcap_event_name\n1,1,raw"
                    headers = {'content-type': 'text/csv; charset=utf-8'}
                    return (201, headers, resp)
                else:
                    resp = [{"field_name":"record_id"}, {"field_name":"test"}]

            return (201, headers, json.dumps(resp))

        responses.add_callback(
            responses.POST,
            self.long_proj_url,
            callback=request_callback_long,
            content_type="application/json",
        )

    def add_normalproject_response(self):
        def request_callback_normal(request):
            parsed = urlparse.urlparse("?{}".format(request.body))
            data = urlparse.parse_qs(parsed.query)
            headers = {"Content-Type": "application/json"}

            if " filename" in data:
                resp = {}
            else:
                request_type = data.get("content", ['unknown'])[0]

                if "returnContent" in data:
                    if "non_existent_key" in data["data"][0]:
                        resp = {"error": "invalid field"}
                    else:
                        resp = {"count": 1}
                elif (request_type == "metadata"):
                    if "csv" in data["format"]:
                        resp = "field_name,field_label,form_name,arm_num,name\n"\
                            "record_id,Record ID,Test Form,1,test\n"
                        headers = {'content-type': 'text/csv; charset=utf-8'}
                        return (201, headers, resp)

                    else:
                        resp = [{
                            'field_name': 'record_id',
                            'field_label': 'Record ID',
                            'form_name': 'Test Form',
                            "arm_num": 1,
                            "name": "test",
                            "field_type": "text",
                        }, {
                            'field_name': 'file',
                            'field_label': 'File',
                            'form_name': 'Test Form',
                            "arm_num": 1,
                            "name": "file",
                            "field_type": "file",
                        }, {
                            'field_name': 'dob',
                            'field_label': 'Date of Birth',
                            'form_name': 'Test Form',
                            "arm_num": 1,
                            "name": "dob",
                            "field_type": "date",
                        }]
                elif (request_type == "version"):
                    resp = {
                        'error': "no version info"
                    }
                elif (request_type == "event"):
                    resp = {
                        'error': "no events"
                    }
                elif (request_type == "arm"):
                    resp = {
                        'error': "no arm"
                    }
                elif (request_type == "record"):
                    if "csv" in data["format"]:
                        resp = "record_id,test,first_name,study_id\n1,1,Peter,1"
                        headers = {'content-type': 'text/csv; charset=utf-8'}
                        return (201, headers, resp)
                    elif "exportDataAccessGroups" in data:
                        resp = [
                            {"field_name":"record_id", "redcap_data_access_group": "group1"},
                            {"field_name":"test", "redcap_data_access_group": "group1"}
                        ]
                    elif "label" in data.get("rawOrLabel"):
                        resp = [{"matcheck1___1": "Foo"}]
                    else:
                        resp = [
                            {"record_id": "1", "test": "test1"},
                            {"record_id": "2", "test": "test"}
                        ]
                elif (request_type == "file"):
                    resp = {}
                    headers["content-type"] = "text/plain;name=data.txt"
                elif (request_type == "user"):
                    resp = [
                        {
                            'firstname': "test",
                            'lastname': "test",
                            'email': "test",
                            'username': "test",
                            'expiration': "test",
                            'data_access_group': "test",
                            'data_export': "test",
                            'forms': "test"
                        }
                    ]

            return (201, headers, json.dumps(resp))

        responses.add_callback(
            responses.POST,
            self.normal_proj_url,
            callback=request_callback_normal,
            content_type="application/json",
        )

    def add_ssl_project(self):
        def request_callback_ssl(request):
            parsed = urlparse.urlparse("?{}".format(request.body))
            data = urlparse.parse_qs(parsed.query)

            request_type = data["content"][0]
            if (request_type == "metadata"):
                resp = [{
                    'field_name': 'record_id',
                    'field_label': 'Record ID',
                    'form_name': 'Test Form',
                    "arm_num": 1,
                    "name": "test"
                }]
            if (request_type == "version"):
                resp = {
                    'error': "no version info"
                }
            if (request_type == "event"):
                resp = {
                    'error': "no events"
                }
            if (request_type == "arm"):
                resp = {
                    'error': "no arm"
                }

            headers = {"Content-Type": "application/json"}
            return (201, headers, json.dumps(resp))

        responses.add_callback(
            responses.POST,
            self.ssl_proj_url,
            callback=request_callback_ssl,
            content_type="application/json",
        )

    def add_survey_project(self):
        def request_callback_survey(request):
            parsed = urlparse.urlparse("?{}".format(request.body))
            data = urlparse.parse_qs(parsed.query)

            request_type = data["content"][0]
            if (request_type == "metadata"):
                resp = [{
                    'field_name': 'record_id',
                    'field_label': 'Record ID',
                    'form_name': 'Test Form',
                    "arm_num": 1,
                    "name": "test"
                }]
            elif (request_type == "version"):
                resp = {
                    'error': "no version info"
                }
            elif (request_type == "event"):
                resp = {
                    'error': "no events"
                }
            elif (request_type == "arm"):
                resp = {
                    'error': "no arm"
                }
            elif (request_type == "record"):
                resp = [
                    {"field_name":"record_id", "redcap_survey_identifier": "test", "demographics_timestamp": "a_real_date"},
                    {"field_name":"test", "redcap_survey_identifier": "test", "demographics_timestamp": "a_real_date"}
                ]

            headers = {"Content-Type": "application/json"}
            return (201, headers, json.dumps(resp))

        responses.add_callback(
            responses.POST,
            self.survey_proj_url,
            callback=request_callback_survey,
            content_type="application/json",
        )

    @responses.activate
    def create_projects(self):
        self.add_long_project_response()
        self.add_normalproject_response()
        self.add_ssl_project()
        self.add_survey_project()

        self.long_proj = Project(self.long_proj_url, self.reg_token)
        self.reg_proj = Project(self.normal_proj_url, self.reg_token)
        self.ssl_proj = Project(self.ssl_proj_url, self.reg_token, verify_ssl=False)
        self.survey_proj = Project(self.survey_proj_url, self.reg_token)


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

    @responses.activate
    def test_json_export(self):
        """ Make sure we get a list of dicts"""
        self.add_normalproject_response()
        data = self.reg_proj.export_records()
        self.assertIsInstance(data, list)
        for record in data:
            self.assertIsInstance(record, dict)

    @responses.activate
    def test_long_export(self):
        """After determining a unique event name, make sure we get a
        list of dicts"""
        self.add_long_project_response()
        unique_event = self.long_proj.events[0]['unique_event_name']
        data = self.long_proj.export_records(events=[unique_event])
        self.assertIsInstance(data, list)
        for record in data:
            self.assertIsInstance(record, dict)

    @responses.activate
    def test_import_records(self):
        "Test record import"
        self.add_normalproject_response()
        data = self.reg_proj.export_records()
        response = self.reg_proj.import_records(data)
        self.assertIn('count', response)
        self.assertNotIn('error', response)

    @responses.activate
    def test_import_exception(self):
        "Test record import throws RedcapError for bad import"
        self.add_normalproject_response()
        data = self.reg_proj.export_records()
        data[0]['non_existent_key'] = 'foo'
        with self.assertRaises(RedcapError) as cm:
            self.reg_proj.import_records(data)
        exc = cm.exception
        self.assertIn('error', exc.args[0])

    def is_good_csv(self, csv_string):
        "Helper to test csv strings"
        return isinstance(csv_string, basestring)

    @responses.activate
    def test_csv_export(self):
        """Test valid csv export """
        self.add_normalproject_response()
        csv = self.reg_proj.export_records(format='csv')
        self.assertTrue(self.is_good_csv(csv))

    @responses.activate
    def test_metadata_export(self):
        """Test valid metadata csv export"""
        self.add_normalproject_response()
        csv = self.reg_proj.export_metadata(format='csv')
        self.assertTrue(self.is_good_csv(csv))

    def test_bad_creds(self):
        "Test that exceptions are raised with bad URL or tokens"
        with self.assertRaises(RedcapError):
            Project(self.bad_url, self.reg_token)
        with self.assertRaises(RedcapError):
            Project(self.bad_url, '1')

    @responses.activate
    def test_fem_export(self):
        """ Test fem export in json format gives list of dicts"""
        self.add_long_project_response()
        fem = self.long_proj.export_fem(format='json')
        self.assertIsInstance(fem, list)
        for arm in fem:
            self.assertIsInstance(arm, dict)

    @responses.activate
    def test_file_export(self):
        """Test file export and proper content-type parsing"""
        self.add_normalproject_response()
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

    def import_file(self):
        upload_fname = self.upload_fname()
        with open(upload_fname, 'r') as fobj:
            response = self.reg_proj.import_file('1', 'file', upload_fname, fobj)
        return response

    def upload_fname(self):
        import os
        this_dir, this_fname = os.path.split(__file__)
        return os.path.join(this_dir, 'data.txt')

    @responses.activate
    def test_file_import(self):
        "Test file import"
        self.add_normalproject_response()
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

    @responses.activate
    def test_file_delete(self):
        "Test file deletion"
        self.add_normalproject_response()
        # make sure deleting doesn't raise
        try:
            self.reg_proj.delete_file('1', 'file')
        except RedcapError:
            self.fail("Shouldn't throw RedcapError for successful deletes")

    @responses.activate
    def test_user_export(self):
        "Test user export"
        self.add_normalproject_response()
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

    @responses.activate
    def test_export_data_access_groups(self):
        """Test we get 'redcap_data_access_group' in exported data"""
        self.add_normalproject_response()
        records = self.reg_proj.export_records(export_data_access_groups=True)
        for record in records:
            self.assertIn('redcap_data_access_group', record)
        # When not passed, that key shouldn't be there
        records = self.reg_proj.export_records()
        for record in records:
            self.assertNotIn('redcap_data_access_group', record)

    @responses.activate
    def test_export_survey_fields(self):
        """Test that we get the appropriate survey keys in the exported
        data.

        Note that the 'demographics' form has been setup as the survey
        in the `survey_proj` project. The _timestamp field will vary for
        users as their survey form will be named differently"""
        self.add_survey_project()
        self.add_normalproject_response()
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
    @responses.activate
    def test_metadata_to_df(self):
        """Test metadata export --> DataFrame"""
        self.add_normalproject_response()
        df = self.reg_proj.export_metadata(format='df')
        self.assertIsInstance(df, pd.DataFrame)

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    @responses.activate
    def test_export_to_df(self):
        """Test export --> DataFrame"""
        self.add_normalproject_response()
        self.add_long_project_response()
        df = self.reg_proj.export_records(format='df')
        self.assertIsInstance(df, pd.DataFrame)
        # Test it's a normal index
        self.assertTrue(hasattr(df.index, 'name'))
        # Test for a MultiIndex on longitudinal df
        long_df = self.long_proj.export_records(format='df', event_name='raw')
        self.assertTrue(hasattr(long_df.index, 'names'))

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    @responses.activate
    def test_export_df_kwargs(self):
        """Test passing kwargs to export DataFrame construction"""
        self.add_normalproject_response()
        df = self.reg_proj.export_records(format='df',
            df_kwargs={'index_col': 'first_name'})
        self.assertEqual(df.index.name, 'first_name')
        self.assertTrue('study_id' in df)

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    @responses.activate
    def test_metadata_df_kwargs(self):
        """Test passing kwargs to metadata DataFrame construction"""
        self.add_normalproject_response()
        df = self.reg_proj.export_metadata(format='df',
            df_kwargs={'index_col': 'field_label'})
        self.assertEqual(df.index.name, 'field_label')
        self.assertTrue('field_name' in df)

    @unittest.skipIf(skip_pd, "Couldn't import pandas")
    @responses.activate
    def test_import_dataframe(self):
        """Test importing a pandas.DataFrame"""
        self.add_normalproject_response()
        self.add_long_project_response()
        df = self.reg_proj.export_records(format='df')
        response = self.reg_proj.import_records(df)
        self.assertIn('count', response)
        self.assertNotIn('error', response)
        long_df = self.long_proj.export_records(event_name='raw', format='df')
        response = self.long_proj.import_records(long_df)
        self.assertIn('count', response)
        self.assertNotIn('error', response)

    @responses.activate
    def test_date_formatting(self):
        """Test date_format parameter"""
        self.add_normalproject_response()

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

    @responses.activate
    def test_export_checkbox_labels(self):
        """Testing the export of checkbox labels as field values"""
        self.add_normalproject_response()
        self.assertEqual(
            self.reg_proj.export_records(
                raw_or_label='label',
                export_checkbox_labels=True)[0]['matcheck1___1'],
                'Foo'
        )

    @responses.activate
    def test_export_always_include_def_field(self):
        """ Ensure def_field always comes in the output even if not explicity
        given in a requested form """
        self.add_normalproject_response()
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
