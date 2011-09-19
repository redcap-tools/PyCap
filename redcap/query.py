#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import operator as op
import time


class Query(object):
    """Main class abstracting one single query"""
    cmp_map = {'eq': op.eq, 'ne': op.ne, 'gt': op.gt, 'ge': op.ge, 'le': op.le,
                    'lt': op.lt}

    def __init__(self, field_name, comparisons, qtype='number'):
        """ Constructor

        Parameters
        ----------
        field_name: str
            string corresponding to the field for comparisons
        comparisons: dict
            each key is a "verb" from the following:
                'eq', 'ne', 'le', 'lt', 'ge', 'gt'
            and value is the value of the comparison
        qtype: 'number' | 'integer' | 'date_ymd'
            The assumed type of data for this field_name. Values are casted
            based on this.
        """
        self.fname = field_name
        self.cmps = comparisons
        for k, _ in self.cmps.items():
            if k not in self.cmp_map:
                raise ValueError("Bad comparison verb in constructor")
        self.type = qtype

    def __str__(self):
        """How to print Queries"""
        log = ' AND '.join(['%s:%s' % (comp, v) for
                            comp, v in self.cmps.items()])
        return '%s %s' % (self.fname, log)

    def filter(self, data, return_key, qtype=''):
        """ Filter the data through this Query

        Parameters
        ----------
        data: seq of dicts
            assumed that each dict contains a key of the Query's field name
        return_key: dict key
            assumed that each dict also contains this key
            this key exists in the list of returned dicts
        """
        if qtype:
            typ = qtype
        else:
            typ = self.type
        if typ in ('number', 'integer'):
            xfm = float
        elif typ == 'date_ymd':
            xfm = lambda x: time.strptime(x, '%Y-%m-%d')
        elif typ == 'email':
            raise ValueError("WHY ARE YOU SEARCHING BY EMAIL?")
        else:
            xfm = str
        match = []
        if data:
            sets = []
            for comp, raw_val in self.cmps.items():
                val = xfm(raw_val)
                mat = []
                for row in data:
                    try:
                        new_val = xfm(row[self.fname])
                    except ValueError:  # probably an empty cell
                        pass
                    else:
                        match = self.cmp_map[comp](new_val, val)
                        if match:  # comparison is true
                            mat.append(row[return_key])
                sets.append(set(mat))
            match = list(reduce(lambda a, b: a.intersection(b), sets))
        return match

    def fields(self):
        """ Query and QueryGroup both respond to this method"""
        return [self.fname]


class QueryGroup(object):
    """Class to hold one or more Querys (or QueryGroups!)"""

    def __init__(self, query):
        """ Constructor

        Parameters
        ----------
        query: Query | QueryGroup
            first query object
        """
        self.queries = [query]
        self.logic = []
        self.index = 0
        self.total = 1

    def __str__(self):
        """Print a QueryGroup"""
        all_logic = self.logic[:]
        if len(self.queries) > 1:
            log = ''
            #  Because there's one less logic verb than queries
            all_logic.append('')
            for qry, logic in zip(self.queries, all_logic):
                if isinstance(qry, QueryGroup):
                    fmt = '(%s %s) '
                else:
                    fmt = '%s %s '
                log += fmt % (qry.__str__(), logic)
            return log
        else:
            return self.queries[0].__str__()

    def add_query(self, query, logic='AND'):
        """Add a query to the group

        Parameters
        ----------
        query:  Query | QueryGroup
            query to add
        logic:  'AND' | 'OR'
            logic connecting this query to the last
        """
        self.queries.append(query)
        if logic.upper() not in ('AND', 'OR'):
            raise ValueError('Queries can only be connectd with AND | OR')
        self.logic.append(logic)
        self.total += 1

    def __iter__(self):
        """ So QueryGroup is an iterator"""
        return self

    def next(self):
        """ So we can loop through a QueryGroup """
        if self.index == self.total:
            raise StopIteration
        next_q = self.queries[self.index]
        self.index = self.index + 1
        return next_q

    def fields(self):
        """Returns a list of keys of all the field names referenced by the
        queries in the group"""
        keys = []
        for qry in self.queries:
            fields = qry.fields()
            keys.extend(fields)
        return keys

    def filter(self, data, return_key):
        """ Filter for the query group """
        match = []
        for i, qry in enumerate(self.queries):
            temp_match = set(qry.filter(data, return_key))
            if i == 0:
                # first, set match == to set
                match = temp_match
            else:
                logic = self.logic[i - 1]
                if logic == 'AND':
                    match = match & temp_match
                else:
                    match = match | temp_match
        return list(match)
