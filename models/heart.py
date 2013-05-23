from google.appengine.ext import db
import datetime


class Heart(db.Model):
    title = db.StringProperty(default='')
    created = db.DateTimeProperty(auto_now_add=True)
    last_pulse = db.DateTimeProperty(auto_now_add=True)
    threshold = db.IntegerProperty(default=0)

    def registerPulse(self):
        flatline = self.getActiveFlatline()
        if flatline is not None:
            flatline.active = False
            flatline.end = datetime.datetime.now()
            flatline.put()
        self.last_pulse = datetime.datetime.now()
        self.put()

    def getActiveFlatline(self):
        return Flatline.all().ancestor(self.key()).filter("active =", True).get()

    def checkFlatLine(self):
        active = self.getActiveFlatline()
        if active is not None:
            return

        if self.last_pulse + datetime.timedelta(seconds=self.threshold*2) > datetime.datetime.now():
            return
        Flatline(parent=self).put()


class Flatline(db.Model):
    start = db.DateTimeProperty(auto_now_add=True)
    active = db.BooleanProperty(default=True)
    end = db.DateTimeProperty()
