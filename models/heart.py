from google.appengine.ext import db
from google.appengine.api import users
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
    maintenance_day = db.DateProperty(default=None)
    last_closed_reason = db.StringProperty(default='')

    def register_pulse(self):
        flatline = self.get_active_flatline()
        if flatline is not None:
            flatline.resuscitate()
        self.last_pulse = datetime.utcnow()
        self.put()

    def get_active_flatline(self):
        return Flatline.all().ancestor(self.key()).filter("active =", True).get()

    def check_flatLine(self):
        if self.threshold == 0 or self.cron == '':
            return

        active = self.get_active_flatline()
        if active is not None:
            return

        if not self.is_flatlined():
            return
        f = Flatline(parent=self)
        f.start = self.last_pulse
        f.put()
        flatline_mail(self)

    def is_flatlined(self, utcnow=None):
        if self.cron == '':
            return self.last_pulse + timedelta(seconds=self.threshold*2) < datetime.utcnow()

        # return false if today is maintenance day
        if self.maintenance_day is not None and self.maintenance_day.strftime('%Y-%m-%d') == local_time_zone.localize(datetime.utcnow()).strftime('%Y-%m-%d'):
            return False

        offset = timedelta(seconds=self.threshold)
        if utcnow is not None:
            tznow = pytz.utc.localize(utcnow.replace(tzinfo=None)).astimezone(self.tz())
        else:
            tznow = self.tznow()

        (next_date, next_next_date) = self.get_next_local_pulse_dates()

        # flatline if next_date and last_pulse are outside offset 
        if abs((next_date - self.localized_last_pulse()).total_seconds()) < self.threshold:
            return next_next_date + offset < tznow

        return  next_date + offset < tznow

    def localized_last_pulse(self):
        # Make sure last is native datetime to avoid ValueError, 'Not naive datetime (tzinfo is already set)
        last = self.last_pulse.replace(tzinfo=None)
        return pytz.utc.localize(last).astimezone(self.tz())

    def tz(self):
        return pytz.timezone(self.time_zone or 'UTC')

    def tznow(self):
        return pytz.utc.localize(datetime.utcnow()).astimezone(self.tz())

    def get_next_local_pulse_dates(self):
        if self.cron == '':
            return ( None, None )

        local_time_zone = self.tz()
        
        next_date = croniter(self.cron, self.localized_last_pulse()).get_next(datetime)
        next_date = local_time_zone.localize(next_date)

        next_next_date = croniter(self.cron, next_date).get_next(datetime)
        next_next_date = local_time_zone.localize(next_next_date)

        return next_date, next_next_date

    def calculate_next_flatline(self):
        (next_date, next_next_date) = self.get_next_local_pulse_dates()
        if next_date is None:
            return
        next_date_plus_threshold = next_date + timedelta(seconds=self.threshold)
        next_next_date_minus_threshold = next_next_date - timedelta(seconds=self.threshold)
        next_next_date_plus_threshold = next_next_date + timedelta(seconds=self.threshold)
        
        threshold_end = next_next_date_plus_threshold if next_date_plus_threshold > next_next_date_minus_threshold else next_date_plus_threshold
        flatline = threshold_end + timedelta(microseconds=1)

        return flatline.astimezone(pytz.utc)

    def check_maintenance(self):
        # Clear active flatline if today is maintenance day
        if datetime.today().date() != self.maintenance_day:
            return
        dayAfterMaintenanceDay = datetime.combine(datetime.today().date() + timedelta(days=1), datetime.min.time())
        self.last_pulse = dayAfterMaintenanceDay
        active_flatline = self.get_active_flatline()
        if active_flatline is None:
            return
        active_flatline.close()
        self.last_closed_reason = active_flatline.closed_reason
        active_flatline.put()

    def check_deactivation(self, threshold):
        # Clear active flatline if threshold is set to zero
        if threshold == self.threshold or threshold != 0:
            return

        current_user = users.get_current_user()
        self.last_closed_reason = "Deactivated by " + current_user.nickname()

        active_flatline = self.get_active_flatline()
        if active_flatline is None:
            return
        active_flatline.close()
        active_flatline.put()


class Flatline(db.Model):
    start = db.DateTimeProperty(auto_now_add=True)
    active = db.BooleanProperty(default=True)
    end = db.DateTimeProperty()
    closed_reason = db.StringProperty(default='')
    closed_by_user = db.StringProperty(default='')

    def resuscitate(self):
        self.active = False
        self.end = datetime.now()
        self.closed_reason = "Pulse received"
        heart = self.parent()
        heart.last_closed_reason = self.closed_reason
        resuscitate_mail(self.parent())

        heart.put()
        self.put()

    def close(self):
        self.active = False
        self.end = datetime.now()
        self.closed_reason = "Maintenance"
        current_user = users.get_current_user()
        if current_user:
            self.closed_by_user = current_user.nickname()

        self.put()
