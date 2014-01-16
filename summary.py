#!/usr/bin/env python
import webapp2
import json
from models.organization import Organization
from models.heart import Heart, Flatline


def indextransform(org):
    return {
        'title': org.title or org.key().id_or_name(),
        'key': org.key().id_or_name(),
    }


def flatlinetransform(f):
    return {
        'start': str(f.start),
        'heart': f.parent().key().id_or_name(),
        'title': f.parent().title
    }


class SummaryHandler(webapp2.RequestHandler):
    def get(self):
        id = int(self.request.url.rsplit('/', 1)[1])
        org = Organization.get_by_id(id)
        newhearts = Heart.all().ancestor(org.key()).filter('title =', '').fetch(2000)
        flatlines = Flatline.all().filter("active =", True).fetch(2000)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({
            'newhearts': map(indextransform, newhearts),
            'flatlines': map(flatlinetransform, flatlines),
        }))


app = webapp2.WSGIApplication([
    ('/summaries/.*', SummaryHandler)
], debug=True)