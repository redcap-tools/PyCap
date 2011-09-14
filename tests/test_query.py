#! /usr/bin/env python

import unittest

from redcap import Query, QueryGroup


class QueryTests(unittest.TestCase):
    """ Query Test Cases """

    def setUp(self):
        self.data = [{'id': str(i), 'age': a, 'score': s} for i, a, s in
                        zip(range(1, 6), range(12, 2, -2), range(10, 60, 10))]

    def tearDown(self):
        del self.data

    def test_bad_comp(self):
        with self.assertRaises(ValueError):
            Query('subjage', {'ze': '12'})

    def test_good_comp(self):
        good_cmp = {'le': 10, 'lt': 10, 'gt': 1, 'ge': 1, 'ne': 5, 'eq': 6}
        field = 'score'
        q = Query(field, good_cmp)
        self.assertIsInstance(q, Query)

    def test_filter(self):
        q = Query('age', {'gt': 8}, 'number')
        self.assertEqual(len(q.filter(self.data, 'id')), 2)

    def test_groupfilter_and(self):
        q1 = Query('age', {'ge': 5})
        q2 = Query('score', {'lt': 40})
        q = QueryGroup(q1)
        q.add_query(q2, 'AND')
        self.assertEqual(len(q.filter(self.data, 'id')), 3)

    def test_groupfilter_or(self):
        q1 = Query('age', {'ge': 5})
        q2 = Query('score', {'lt': 70})
        q = QueryGroup(q1)
        q.add_query(q2, 'OR')
        self.assertEqual(len(q.filter(self.data, 'id')), 5)
