#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from redcap import RCRequest, RCAPIError


class TestClass(unittest.TestCase):
    """ Testing RCRequest """

    def setUp(self):
        """ We can use Kenneth Reitz's httpbin.org to test requests """
        self.url = 'http://httpbin.org'
        self.base = {'token': '8E66DB6844D58E990075AFB51658A002',
                     'format': 'json',
                     'type': 'flat'}
        self.badmd = {'token': 'B82CB05641E3BE8247E5F852EAFC5C21',
                        'format': 'json',
                        'type': 'flat',
                        'content': 'metadata'}

    def tearDown(self):
        pass

    def test_md_content(self):
        """Test that RCRequest throws correctly for malformed payloads"""
        pl = self.base
        ags = [self.url, pl, 'metadata']
        #  no 'content' key
        self.assertRaises(RCAPIError, RCRequest, *ags)
        #  wrong content
        pl['content'] = 'blahblah'
        self.assertRaises(RCAPIError, RCRequest, *ags)
        #  good content
        pl['content'] = 'metadata'
        r = RCRequest(*ags)
        self.assertIsInstance(r, RCRequest)

    def test_bad_md(self):
        """Test that newlines are appropriately dealt with"""
        args = ['https://redcap.vanderbilt.edu/api/', self.badmd, 'metadata']
        r = RCRequest(*args).execute()
        self.assertTrue(r is not None)
        self.assertTrue(len(r) > 0)

    def test_survey_participant_list_type(self):
        payload = {
            'token': 'foobar',
            'content': 'participantList',
            'format': 'json',
            'instrument': 'bar',
        }
        url = 'https://foobarbat.com'
        typee = 'exp_survey_participant_list'
        # This should not raise
        RCRequest(url, payload, typee)

        # This should raise because of a different content
        payload['content'] = 'foobar'
        with self.assertRaises(RCAPIError):
            RCRequest(url, payload, typee)
