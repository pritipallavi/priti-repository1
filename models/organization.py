from google.appengine.ext import db
from models.heart import Heart


class Organization(db.Model):
    title = db.StringProperty()
    users = db.StringListProperty()

    def get_heart(self, id):
        return Heart.get_or_insert(id, parent=self)
