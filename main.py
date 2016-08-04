#!/usr/bin/env python

# name: Andrew Wang, intern
# Analytics Pros
# Connect App Engine with GA

import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
    	self.response.headers['Content-Type'] = 'text/plain'
    	self.response.write('Hello, test new name thing')

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)