from google.appengine.ext import db
from datetime import datetime, timedelta
from models import resuscitate_mail, flatline_mail
from lib.croniter import croniter
from pytz.gae import pytz


class Heart(db.Model):
    title = db.StringProperty(default='')
    created = db.DateTimeProperty(auto_now_add=True)
    last_pulse = db.DateTimeProperty(auto_now_add=True)
    threshold = db.IntegerProperty(default=0)
    cron = db.StringProperty(default='')
    time_zone = db.StringProperty(default='UTC')

    def registerPulse(self):
        flatline = self.getActiveFlatline()
        if flatline is not None:
            flatline.resuscitate()
        self.last_pulse = datetime.now()
        self.put()

    def getActiveFlatline(self):
        return Flatline.all().ancestor(self.key()).filter("active =", True).get()

    def checkFlatLine(self):
        if self.threshold == 0 or self.cron == '':
            return

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
        if self.cron == '':
            return self.last_pulse + timedelta(seconds=self.threshold*2) < datetime.utcnow()

        if self.time_zone is None:
            self.time_zone = 'UTC'

        local_time_zone = pytz.timezone(self.time_zone)
        offset = timedelta(seconds=self.threshold)
        last_pulse_local = pytz.utc.localize(self.last_pulse).astimezone(local_time_zone)
        next_date = croniter(self.cron, last_pulse_local).get_next(datetime)

        return local_time_zone.localize(next_date).astimezone(pytz.utc) + offset < pytz.utc.localize(datetime.utcnow())


class Flatline(db.Model):
    start = db.DateTimeProperty(auto_now_add=True)
    active = db.BooleanProperty(default=True)
    end = db.DateTimeProperty()

    def resuscitate(self):
        self.active = False
        self.end = datetime.now()
        resuscitate_mail(self.parent())

        self.put()
