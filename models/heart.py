from google.appengine.ext import db
import datetime
from models import resuscitate_mail, flatline_mail
from lib.croniter import croniter


class Heart(db.Model):
    title = db.StringProperty(default='')
    created = db.DateTimeProperty(auto_now_add=True)
    last_pulse = db.DateTimeProperty(auto_now_add=True)
    threshold = db.IntegerProperty(default=0)
    cron = db.StringProperty(default='')

    def registerPulse(self):
        flatline = self.getActiveFlatline()
        if flatline is not None:
            flatline.resuscitate()
        self.last_pulse = datetime.datetime.now()
        self.put()

    def getActiveFlatline(self):
        return Flatline.all().ancestor(self.key()).filter("active =", True).get()

    def checkFlatLine(self):
        active = self.getActiveFlatline()
        if active is not None:
            return

        if not self.is_flatlined():
            return
        f = Flatline(parent=self)
        f.start = self.last_pulse
        f.put()
        flatline_mail(self)

    def is_flatlined(self):
        if self.cron != '':
            return croniter(self.cron, self.last_pulse).get_next(datetime) + datetime.timedelta(seconds=self.threshold) < datetime.datetime.now()
        return self.last_pulse + datetime.timedelta(seconds=self.threshold*2) < datetime.datetime.now()


class Flatline(db.Model):
    start = db.DateTimeProperty(auto_now_add=True)
    active = db.BooleanProperty(default=True)
    end = db.DateTimeProperty()

    def resuscitate(self):
        self.active = False
        self.end = datetime.datetime.now()
        resuscitate_mail(self.parent())
        self.put()
