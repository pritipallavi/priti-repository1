from google.appengine.ext import db
from models.pulse import Pulse
import datetime


class Heart(db.Model):
    title = db.StringProperty()
    id = db.StringProperty()
    last_pulse = db.DateTimeProperty(auto_now_add=True)
    threshold = db.IntegerProperty(default=5*60)

    def registerPulse(self):
        pulse = Pulse(parent=self)
        pulse.put()
        self.last_pulse = datetime.datetime.now()
        self.put()
