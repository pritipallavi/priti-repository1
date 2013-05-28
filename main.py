#!/usr/bin/env python
import webapp2
import json
from google.appengine.api import users
from models.organization import Organization, Invitation
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
        self.response.out.write(json.dumps({'title': org.title, 'key': org.key.id_or_name()}))


class SummaryHandler(webapp2.RequestHandler):
    def get(self):
        id = int(self.request.url.rsplit('/', 1)[1])
        org = Organization.get_by_id(id)
        newhearts = Heart.all().ancestor(org.key()).filter('title =', '').fetch(2000)
        flatlines = Flatline.all().filter("active =", True).fetch(2000)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({
            'title': org.title,
            'newhearts': map(indextransform, newhearts),
            'flatlines': map(flatlinetransform, flatlines),
            'users': org.users
        }))


class HeartHandler(webapp2.RequestHandler):
    def get(self):
        id = int(self.request.url.rsplit('/', 3)[1])
        org = Organization.get_by_id(id)
        key = self.request.url.rsplit('/', 1)[1]
        heart = Heart.get_by_key_name(key, parent=org)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'title': heart.title or heart.key().id_or_name(), 'threshold': heart.threshold, 'last_pulse': str(heart.last_pulse)}))

    def put(self):
        payload = json.loads(self.request.body)
        id = int(self.request.url.rsplit('/', 3)[1])
        org = Organization.get_by_id(id)
        key = self.request.url.rsplit('/', 1)[1]
        heart = Heart.get_by_key_name(key, parent=org)
        heart.title = str(payload['title'])
        heart.threshold = int(payload['threshold'])
        heart.put()


class InvitationHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.url.rsplit('/', 1)[1]
        inv = Invitation.get(id)
        self.response.out.write(json.dumps({'title': inv.parent().title}))

    def post(self):
        payload = json.loads(self.request.body)
        org = Organization.get_by_id(int(payload['organization']))
        inv = Invitation(parent=org)
        inv.email = payload['email']
        inv.put()
        inv.send()


class InvitationAcceptHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.url.rsplit('/', 2)[1]
        print id
        inv = Invitation.get(id)
        inv.accept()


class InvitationDeclineHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.url.rsplit('/', 2)[1]
        print id
        inv = Invitation.get(id)
        inv.decline()


app = webapp2.WSGIApplication([
    ('/api/me/organizations', OrganizationHandler),
    ('/api/organizations/.*/hearts/.*', HeartHandler),
    ('/api/invitations/.*/accept', InvitationAcceptHandler),
    ('/api/invitations/.*/decline', InvitationDeclineHandler),
    ('/api/invitations/.*', InvitationHandler),
    ('/api/organizations/.*', SummaryHandler)
], debug=True)
