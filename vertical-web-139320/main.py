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

import json
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

testData0 = [
    {"day":3, "hour":1, "value":2},
    {"day":3, "hour":2, "value":7},
    {"day":4, "hour":6, "value":14},
    {"day":5, "hour":3, "value":23},
    {"day":6, "hour":5, "value":1},
    {"day":1, "hour":3, "value":5},
    {"day":1, "hour":7, "value":55},
    {"day":1, "hour":10, "value":7},
    {"day":2, "hour":7, "value":2},
    {"day":7, "hour":7, "value":2}
]

testData1 = [
  {"day":1, "hour":1, "value":3}
]

testData2 = [
  {"day":1, "hour":1, "value":3},
  {"day":2, "hour":2, "value":25}
]

testData7 = [
  {"day":1, "hour":1, "value":1},
  {"day":2, "hour":1, "value":2},
  {"day":3, "hour":1, "value":3},
  {"day":4, "hour":1, "value":4},
  {"day":5, "hour":1, "value":5},
  {"day":6, "hour":1, "value":6},
  {"day":7, "hour":1, "value":7},
]

testData7B = [
  {"day":1, "hour":1, "value":1},
  {"day":1, "hour":2, "value":2},
  {"day":1, "hour":3, "value":3},
  {"day":1, "hour":4, "value":4},
  {"day":1, "hour":5, "value":5},
  {"day":1, "hour":6, "value":6},
  {"day":1, "hour":7, "value":7},
]

testData9 = [
  {"day":1, "hour":1, "value":1},
  {"day":1, "hour":2, "value":2},
  {"day":1, "hour":3, "value":3},
  {"day":1, "hour":4, "value":4},
  {"day":1, "hour":5, "value":5},
  {"day":1, "hour":6, "value":6},
  {"day":1, "hour":7, "value":7},
  {"day":1, "hour":8, "value":8},
  {"day":1, "hour":9, "value":9}
]

"""
samples = {
  {
    "name": "7 vertical",
    "data": [
      {"day":1, "hour":1, "value":1},
      {"day":2, "hour":1, "value":2},
      {"day":3, "hour":1, "value":3},
      {"day":4, "hour":1, "value":4},
      {"day":5, "hour":1, "value":5},
      {"day":6, "hour":1, "value":6},
      {"day":7, "hour":1, "value":7}
    ]
  },
  {
    "name": "7 horizontal",
    "data": [
      {"day":1, "hour":1, "value":1},
      {"day":1, "hour":2, "value":2},
      {"day":1, "hour":3, "value":3},
      {"day":1, "hour":4, "value":4},
      {"day":1, "hour":5, "value":5},
      {"day":1, "hour":6, "value":6},
      {"day":1, "hour":7, "value":7}
    ]
  }
}
"""

sampleIndex = 0 #default to 7 vertical
samples =[
  {
    "name":"7 vertical",
    "data": [
      {"day":1, "hour":1, "value":1},
      {"day":2, "hour":1, "value":2},
      {"day":3, "hour":1, "value":3},
      {"day":4, "hour":1, "value":4},
      {"day":5, "hour":1, "value":5},
      {"day":6, "hour":1, "value":6},
      {"day":7, "hour":1, "value":7}
    ]
  },
  {
    "name": "7 horizontal",
    "data": [
      {"day":1, "hour":1, "value":1},
      {"day":1, "hour":2, "value":2},
      {"day":1, "hour":3, "value":3},
      {"day":1, "hour":4, "value":4},
      {"day":1, "hour":5, "value":5},
      {"day":1, "hour":6, "value":6},
      {"day":1, "hour":7, "value":7}
    ]
  }
]

################
currentTest = testData7B
################

class MainHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        # If sample is in the url, use sample data
        if self.request.get("index"):
            #val1 = 1
            #cleanedData = [{"day":3, "hour":1, "value":val1}, {"day":1, "hour":2, "value":13}]
            cleanedData = currentTest

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
        cleanedData = samples[sampleIndex]['data']
        self.response.write(template.render({'cleanedData':cleanedData}))

class SideBySide(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('sidebyside.html')
        self.response.write(template.render({'samples':samples}))

app = webapp2.WSGIApplication([
    ('/', InputHandler),
    ('/results', MainHandler),
    ('/input', InputHandler),
    ('/vegatest', VegaTest),
    ('/sidebyside', SideBySide),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)