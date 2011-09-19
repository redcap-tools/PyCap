#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from urllib2 import URLError
from redcap import RCRequest, RCAPIError

class TestClass(unittest.TestCase):
    """ Testing RCRequest """
    
    def setUp(self):
        """ We can use Kenneth Reitz's httpbin.org to test requests """
        self.url = 'http://httpbin.org'
        self.base = {'token': '8E66DB6844D58E990075AFB51658A002',
                     'format': 'json',
                     'type': 'flat'}
    
    def tearDown(self):
        pass

    def test_badurl(self):
        pl = self.base
        pl['content'] = 'metadata'
        req = RCRequest('http://www.asldkfasdf.com', pl, 'metadata')
        self.assertRaises(URLError, req.execute, *[])
        
    def test_md_content(self):
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
