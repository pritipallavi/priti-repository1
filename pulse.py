#!/usr/bin/env python
#
import webapp2
from models.organization import Organization
from models.heart import Heart


class PulseHandler(webapp2.RequestHandler):
    def get(self):

        id = self.request.get_all('id')[0]
        org = int(self.request.get_all('org')[0])

        h = Organization.get_by_id(org).get_heart(id)
        h.registerPulse()

        self.response.write('ok')


class CheckForFlatlineHandler(webapp2.RequestHandler):
    def get(self):
        hearts = Heart.all().filter('threshold >', 0).fetch(5000)
        for heart in hearts:
            heart.checkFlatLine()
        self.response.write('ok')


app = webapp2.WSGIApplication([
    ('/pulse.*', PulseHandler),
    ('/checkforflatlines.*', CheckForFlatlineHandler)
], debug=True)
