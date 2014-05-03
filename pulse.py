#!/usr/bin/env python
#
import webapp2
from models.organization import Organization
from models.heart import Heart
import datetime


class PulseHandler(webapp2.RequestHandler):
    def get(self):

        id = self.request.get_all('id')[0]
        org = int(self.request.get_all('org')[0])
        if id.find('\\') > 0:
            self.response.write('key must not contain backslash')
            return

        h = Organization.get_by_id(org).get_heart(id)
        h.register_pulse()

        self.response.write('ok')


class CheckForFlatlineHandler(webapp2.RequestHandler):
    def get(self):
        hearts = Heart.all().filter('last_pulse <', datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).fetch(5000)
        for heart in hearts:
            heart.check_flatLine()
        self.response.write('ok')


app = webapp2.WSGIApplication([
    ('/pulse.*', PulseHandler),
    ('/checkforflatlines.*', CheckForFlatlineHandler)
], debug=True)
