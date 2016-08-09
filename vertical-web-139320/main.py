#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
name: Andrew Wang, intern
company: Analytics pros
project: Connect Google Analytics with AppEngine
"""

import os
import webapp2
import httplib2
from apiclient.discovery import build
from google.appengine.ext import webapp
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets

decorator = OAuth2DecoratorFromClientSecrets(
  os.path.join(os.path.dirname(__file__), 'client_secret.json'),
  'https://www.googleapis.com/auth/analytics.readonly')

service = build('analytics', 'v3')

import jinja2
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True, extensions=['jinja2.ext.autoescape'])


class MainHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        # If sample is in the url, use sample data
        if self.request.get("sample"):
            val1 = 1
            cleanedData = [{"day":3, "hour":1, "value":val1}, {"day":1, "hour":2, "value":13}]
        # Otherwise use the GA data
        elif self.request.get("viewId"):
            http = decorator.http()

            report = service.data().ga().get(
              ids='ga:%s'%self.request.get("viewId"),
              metrics='ga:sessions',
              dimensions='ga:hour,ga:dayOfWeek',
              start_date='2014-12-01',
              end_date='2015-12-07').execute(http)

            cleanedData = []
            for row in report['rows']:
                rowDictionary = {"day":int(row[1])+1, "hour":int(row[0]) + 1, "value":int(row[2])}
                cleanedData.append(rowDictionary)
           
        # Neither sample requested nor viewId sent
        else:
            cleanedData = []
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({'cleanedData':cleanedData}))

class InputHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('input.html')
        self.response.write(template.render())

class VegaTest(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
    	template = JINJA_ENVIRONMENT.get_template('vegatest.html')
        cleanedData = [
          {"temp":41.1, "date":"2010/01/01 07:00"},
          {"temp":42.0, "date":"2010/01/01 18:00"},
          {"temp":43.0, "date":"2010/06/11 17:00"},
          {"temp":44.0, "date":"2010/06/12 00:00"},
          {"temp":45.0, "date":"2010/06/14 05:00"},
          {"temp":46.0, "date":"2010/06/22 04:00"},
          {"temp":47.2, "date":"2010/06/27 17:00"},
          {"temp":38.0, "date":"2010/09/28 21:00"},
          {"temp":29.3, "date":"2010/12/03 01:00"}
        ]
        self.response.write(template.render({'cleanedData':cleanedData}))

app = webapp2.WSGIApplication([
    ('/', InputHandler),
    ('/results', MainHandler),
    ('/input', InputHandler),
    ('/vegatest', VegaTest),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)