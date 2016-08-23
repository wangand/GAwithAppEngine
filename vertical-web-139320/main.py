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

sampleIndex = 0 #default dataset to visualize in sidebyside
samples =[
  {
    "name":"Just 1",
    "data": [
        {"day":1, "hour":1, "value":3}
    ]
  },
  {
    "name":"2 vertical",
    "data": [
        {"day":1, "hour":1, "value":1},
        {"day":1, "hour":2, "value":20}
    ]
  },
  {
    "name":"2 horizontal",
    "data": [
        {"day":1, "hour":1, "value":1},
        {"day":2, "hour":1, "value":20}
    ]
  },
  {
    "name":"2x2 grid",
    "data": [
        {"day":1, "hour":1, "value":1},
        {"day":1, "hour":2, "value":20},
        {"day":2, "hour":1, "value":20},
        {"day":2, "hour":2, "value":1}
    ]
  },
  {
    "name":"3 vertical",
    "data": [
        {"day":1, "hour":1, "value":1},
        {"day":1, "hour":2, "value":20},
        {"day":1, "hour":3, "value":30}
    ]
  },
  {
    "name":"3 horizontal",
    "data": [
        {"day":1, "hour":1, "value":1},
        {"day":2, "hour":1, "value":20},
        {"day":3, "hour":1, "value":30}
    ]
  },
  {
    "name":"3x3 grid",
    "data": [
        {"day":1, "hour":1, "value":1},
        {"day":1, "hour":2, "value":20},
        {"day":1, "hour":3, "value":30},
        {"day":2, "hour":1, "value":1},
        {"day":2, "hour":2, "value":20},
        {"day":2, "hour":3, "value":30},
        {"day":3, "hour":1, "value":1},
        {"day":3, "hour":2, "value":20},
        {"day":3, "hour":3, "value":30}
    ]
  },
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
  },
  {
  "name":"9 horizontal",
    "data": [
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
  },
  {
  "name":"random",
    "data": [
      {"day":1, "hour":1, "value":10},
      {"day":1, "hour":10, "value":24},
      {"day":1, "hour":11, "value":3},
      {"day":2, "hour":4, "value":4},
      {"day":2, "hour":5, "value":30},
      {"day":3, "hour":3, "value":25},
      {"day":4, "hour":5, "value":5},
      {"day":5, "hour":1, "value":4},
      {"day":5, "hour":3, "value":17},
      {"day":5, "hour":5, "value":8},
      {"day":6, "hour":5, "value":45},
      {"day":7, "hour":3, "value":6},
      {"day":7, "hour":7, "value":39},
      {"day":7, "hour":8, "value":28},
      {"day":7, "hour":9, "value":29}
    ]
  }
]

class MainHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        # If sample is in the url, use sample data
        if self.request.get("index"):
            #val1 = 1
            #cleanedData = [{"day":3, "hour":1, "value":val1}, {"day":1, "hour":2, "value":13}]
            sampleIndex = int(self.request.get("index"))
            cleanedData = samples[sampleIndex]['data']

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
        if self.request.get("index"):
            sampleIndex = int(self.request.get("index"))

        if self.request.get("spec"):
            spec = self.request.get("spec")
        else:
            spec = "vlSpec"

        template = JINJA_ENVIRONMENT.get_template('vegatest.html')
        cleanedData = samples[sampleIndex]['data']
        self.response.write(template.render({'cleanedData':cleanedData, 'spec':spec}))

class SideBySide(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('sidebyside.html')
        self.response.write(template.render({'samples':samples}))

class VideoTesting(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('videotesting.html')
        self.response.write(template.render())

class CookieTesting(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('cookietest.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', InputHandler),
    ('/results', MainHandler),
    ('/input', InputHandler),
    ('/vegatest', VegaTest),
    ('/sidebyside', SideBySide),
    ('/videotesting', VideoTesting),
    ('/cookietesting', CookieTesting),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)