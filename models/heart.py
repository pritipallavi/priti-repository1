from google.appengine.ext import db
from models.pulse import Pulse


class Heart(db.Model):
    title = db.StringProperty()
    id = db.StringProperty()

    def registerPulse(self):
        pulse = Pulse(parent=self)
        pulse.put()
