from google.appengine.ext import db
from models.heart import Heart
from google.appengine.api import users
from models import invite_mail


class Organization(db.Model):
    title = db.StringProperty()
    users = db.StringListProperty()
    alert_email = db.StringProperty(default='')

    def get_heart(self, id):
        return Heart.get_or_insert(id, parent=self)

    def send_invitation(self, email):
        invi = Invitation(parent=self)
        invi.email = email
        invi.put()
        invi.send()


class Invitation(db.Model):
    email = db.StringProperty()

    def send(self):
        invite_mail(self)

    def accept(self):
        self.parent().users.append(users.get_current_user().email())
        self.parent().put()
        self.delete()

    def decline(self):
        self.delete()
