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
              end_date='2014-12-07').execute(http)

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

app = webapp2.WSGIApplication([
    ('/', InputHandler),
    ('/results', MainHandler),
    ('/input', InputHandler),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)