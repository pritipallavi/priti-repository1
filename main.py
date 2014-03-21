#!/usr/bin/env python
import webapp2
import json
from google.appengine.ext import db
from google.appengine.api import users
from models.organization import Organization, Invitation
from models.heart import Heart, Flatline
from lib.croniter import croniter
from datetime import datetime, timedelta


def indextransform(org):
    return {
        'title': org.title or org.key().id_or_name(),
        'key': org.key().id_or_name(),
    }


def flatlinetransform(f):
    return {
        'end': str(f.end),
        'active': str(f.active),
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
            'users': org.users,
            'alert_email' : org.alert_email,
        }))

    def put(self):
        payload = json.loads(self.request.body)
        id = int(self.request.url.rsplit('/', 1)[1])
        org = Organization.get_by_id(id)
        org.title = str(payload['title'])
        org.alert_email = str(payload['alert_email'])
        org.put()

class ReportHandler(webapp2.RequestHandler):
       def get(self):
        id = int(self.request.url.rsplit('/', 2)[1])
        org = Organization.get_by_id(id)
        rangestart = datetime.utcnow() - timedelta(days=7)
        hearts = Heart.all().ancestor(org.key()).filter('title !=', '').count()
        oldflatlines = Flatline.all().filter("start >", rangestart).fetch(2000)
        oldflatlinesactive = Flatline.all().filter("end >", rangestart).fetch(2000)
        oldflatlines = list(set(oldflatlines) | set(oldflatlinesactive)) 
        alltime = hearts*24*60*60*7 if hearts > 0 else 1
        downtime = sum(map(lambda x: x.seconds, map(lambda x: (x.end if x.end is not None else datetime.utcnow()) - x.start if x.start < rangestart else rangestart,oldflatlines)))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({
            'title': org.title,
            'flatlines': map(flatlinetransform, oldflatlines),
            'availablility' : 1 - float(downtime)/alltime,
            'downtime' : downtime,
            'hearts': hearts
        }))

class HeartHandler(webapp2.RequestHandler):
    def get(self):
        id = int(self.request.url.rsplit('/', 3)[1])
        org = Organization.get_by_id(id)
        key = self.request.url.rsplit('/', 1)[1]
        heart = Heart.get_by_key_name(key, parent=org)
        flatlines = Flatline.all().ancestor(heart).order("-start").fetch(10)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'title': heart.title or heart.key().id_or_name(), 'time_zone': heart.time_zone, 'cron': heart.cron, 'threshold': heart.threshold, 'last_pulse': str(heart.last_pulse), 'flatlines': map(flatlinetransform, flatlines)}))

    def put(self):
        payload = json.loads(self.request.body)
        id = int(self.request.url.rsplit('/', 3)[1])
        org = Organization.get_by_id(id)
        key = self.request.url.rsplit('/', 1)[1]
        heart = Heart.get_by_key_name(key, parent=org)
        heart.title = str(payload['title'])
        heart.threshold = int(payload['threshold'])
        heart.cron = str(payload['cron'])
        heart.time_zone = str(payload['time_zone'])
        croniter(heart.cron)
        heart.put()

    def delete(self):
        id = int(self.request.url.rsplit('/', 3)[1])
        org = Organization.get_by_id(id)
        key = self.request.url.rsplit('/', 1)[1]
        heart = Heart.get_by_key_name(key, parent=org)
        flatlines = Flatline.all(keys_only=True).ancestor(heart).order("-start")
        heart.delete()
        for f in flatlines:
            db.delete(f)


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


class HeartsListHandler(webapp2.RequestHandler):
    def get(self):
        id = int(self.request.url.rsplit('/', 2)[1])
        org = Organization.get_by_id(id)
        hearts = Heart.all().ancestor(org.key()).order("-created").fetch(2000)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({
            'title': org.title,
            'hearts': map(indextransform, hearts)
        }))


app = webapp2.WSGIApplication([
    ('/api/me/organizations', OrganizationHandler),
    ('/api/organizations/.*/report', ReportHandler),
    ('/api/organizations/.*/hearts/.+', HeartHandler),
    ('/api/organizations/.*/hearts', HeartsListHandler),
    ('/api/invitations/.*/accept', InvitationAcceptHandler),
    ('/api/invitations/.*/decline', InvitationDeclineHandler),
    ('/api/invitations/.*', InvitationHandler),
    ('/api/organizations/.*', SummaryHandler)
], debug=True)
