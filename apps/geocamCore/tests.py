# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from xml.dom import minidom

class ValidKmlTest(TestCase):
    def testStartSessionValid(self):
        """
        Tests that querying startSession.kml returns valid XML.
        """
        c = Client()
        response = c.get('/kml/startSession.kml')
        # check for http success status
        self.failUnlessEqual(response.status_code, 200)
        # check response is not empty
        self.failIfEqual("", response.content)
        # check response parses as XML (if not, exception causes failure)
        minidom.parseString(response.content)
