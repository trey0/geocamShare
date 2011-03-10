# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import re
import sys

from django.db.models import Q

from geocamUtil import TimeUtil

class BadQuery(Exception):
    pass

class SearchAbstract:
    # override these settings in derived classes
    getAllFeatures = None
    fields = ()
    fieldAliases = ()
    timeField = 'timestamp'

    def __init__(self):
        self.flookup = dict([(name, name) for name in self.fields])
        self.flookup.update(dict(self.fieldAliases))

    def filterFieldBefore(self, query, clause, field, term, negated):
        if negated:
            raise BadQuery("Oops, can't use minus sign with BEFORE in clause '%s' of search '%s'" % (clause, query))
        try:
            # intervalStart=False to get end of specified interval
            # (inclusive before)
            utcDT = TimeUtil.stringToUtcDT(term, intervalStart=False)
        except ValueError, msg:
            raise BadQuery("Oops, %s in clause '%s' of search '%s'"
                           % (msg, clause, query))
        return Q(**{self.timeField+'__lte': utcDT})

    def filterFieldAfter(self, query, clause, field, term, negated):
        if negated:
            raise BadQuery("Oops, can't use minus sign with AFTER in clause '%s' of search '%s'" % (clause, query))
        try:
            # intervalStart=True to get start of specified interval
            # (inclusive after)
            utcDT = TimeUtil.stringToUtcDT(term, intervalStart=True)
        except ValueError, msg:
            raise BadQuery("Oops, %s in clause '%s' of search '%s'"
                           % (msg, clause, query))
        return Q(**{self.timeField+'__gte': utcDT})

    def filterFieldDefault(self, query, clause, field, term, negated):
        if field == None:
            fields = self.flookup.keys()
        elif field not in self.flookup:
            raise BadQuery("Oops, can't understand field name '%s' of search '%s'.  Legal field names are: %s."
                           % (field, query, ', '.join(self.flookup.keys())))
        else:
            fields = [field]
        if not re.search('^[\.\-\_a-zA-Z0-9]*$', term):
            raise BadQuery("Oops, can't understand term '%s' in search '%s'.  Terms must contain only letters, numbers, periods, hyphens, and underscores."
                           % (term, query))
        if term == '':
            raise BadQuery("Oops, empty search term in clause '%s' of search '%s'."
                           % (clause, query))
        qfilter = Q()
        for f in fields:
            dbField = self.flookup[f]
            qAdd = Q(**{dbField+'__icontains': term})
            if negated:
                qfilter = qfilter & ~qAdd
            else:
                qfilter = qfilter | qAdd
        return qfilter

    def filterField(self, query, clause, field, term, negated):
        if field:
            filterFuncName = 'filterField'+field.capitalize()
            if hasattr(self, filterFuncName):
                filterFunc = getattr(self, filterFuncName)
                return filterFunc(query, clause, field, term, negated)
        return self.filterFieldDefault(query, clause, field, term, negated)
    
    def filterClause(self, query, clause):
        if clause.startswith('-'):
            negated = True
            clause = clause[1:]
        else:
            negated = False
        if ':' in clause:
            field, term = clause.split(':', 1)
            field = field.lower()
        else:
            field, term = None, clause
        return self.filterField(query, clause, field, term, negated)

    def queryTreeToString(self, queryTree):
        return (' OR '
                .join(['(%s)' % (' AND '
                                 .join(['"%s"' % clause
                                        for clause in term]))
                       for term in queryTree]))

    def parseQuery(self, query):
        if not re.search('^[\-\.\:\_a-zA-Z0-9 ]*$', query):
            raise BadQuery("Oops, can't understand search '%s'. Searches must contain only letters, numbers, minus signs, colons, periods, underscores, and spaces."
                           % query)
        queryClauses = query.split()
        #print >>sys.stderr, 'queryClauses:', queryClauses

        queryTree = [[]]
        for clause in queryClauses:
            if clause.lower() == 'or':
                if queryTree[-1] == []:
                    raise BadQuery("Oops, 'or' must come between normal clauses in search '%s'" % query)
                queryTree.append([])
            elif clause.lower() == 'and':
                if queryTree[-1] == []:
                    raise BadQuery("Oops, 'and' must come between normal clauses in search '%s'")
                # ignore -- 'and' is default connective
            else:
                queryTree[-1].append(clause)
        #print >>sys.stderr, 'queryTree:', queryTreeToString(queryTree)
        return queryTree

    def treeToFilter(self, query, queryTree):
        queryFilter = Q()
        for term in queryTree:
            termFilter = Q()
            for clause in term:
                clauseFilter = self.filterClause(query, clause)
                termFilter = termFilter & clauseFilter
            queryFilter = queryFilter | termFilter
        return queryFilter
    
    def searchFeatures0(self, startSet, query):
        queryTree = self.parseQuery(query)
        queryFilter = self.treeToFilter(query, queryTree)
        return startSet.filter(queryFilter)

    def searchFeatures(self, startSet, query):
        result = startSet
        if query:
            result = self.searchFeatures0(result, query)
        return result.distinct().order_by('-'+self.timeField)
