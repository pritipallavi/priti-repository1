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
import webapp2
import json
from google.appengine.api import users
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


class OrganizationHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        orgs = Organization.all().filter('users =', user.email())
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(map(indextransform, orgs)))

    def post(self):
        payload = json.loads(self.request.body)
        org = Organization(title=payload['title'])
        org.users = [users.get_current_user().email()]
        org.key = org.put()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'title': org.title, 'key':org.key.id_or_name()}))


class SummaryHandler(webapp2.RequestHandler):
    def get(self):
        id = int(self.request.url.rsplit('/', 1)[1])
        org = Organization.get_by_id(id)
        newhearts = Heart.all().ancestor(org.key()).filter('title =', '').fetch(2000)
        flatlines = Flatline.all().filter("active =", True).fetch(2000)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'title': org.title, 'newhearts': map(indextransform, newhearts), 'flatlines': map(flatlinetransform, flatlines)}))


class HeartHandler(webapp2.RequestHandler):
    def get(self):
        id = int(self.request.url.rsplit('/', 3)[1])
        org = Organization.get_by_id(id)
        key = self.request.url.rsplit('/', 1)[1]
        heart = Heart.get_by_key_name(key, parent=org)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'title': id, 'threshold': heart.threshold, 'last_pulse': str(heart.last_pulse)}))


app = webapp2.WSGIApplication([
    ('/api/me/organizations', OrganizationHandler),
    ('/api/organizations/.*/hearts/.*', HeartHandler),
    ('/api/organizations/.*', SummaryHandler)
], debug=True)
