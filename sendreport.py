#!/usr/bin/env python
#
import webapp2
from models.organization import Organization
from models.heart import Heart, Flatline
from datetime import datetime, timedelta
from google.appengine.api import mail


def send_report(org, rangestart):
    hearts = Heart.all().ancestor(org.key()).filter('title !=', '').count()
    oldflatlines = Flatline.all().filter("start >", rangestart).order("-start").fetch(2000)
    oldflatlinesactive = Flatline.all().filter("end >", rangestart).order("-end").fetch(2000)
    oldflatlines = list(set(oldflatlines) | set(oldflatlinesactive)) 
    alltime = hearts*24*60*60*7 if hearts > 0 else 1
    downtime = sum(map(lambda x: x.seconds, map(lambda x: (x.end if x.end is not None else datetime.utcnow()) - (x.start if x.start < rangestart else rangestart),oldflatlines)))
    availablility = 1 - float(downtime)/alltime;
   
    message = mail.EmailMessage(sender="alerts@heartrate-monitor.appspotmail.com",
                                subject=org.title + " weekly report")

    message.to = map(lambda user: user, org.users)
    message.body = """
    Here is the weekly report of how your hearts are doing.

    Availablility: """+str(availablility)+"""
    Downtime: """+str(downtime)+"""
    Flatlines: """+str(oldflatlines.__len__)+"""

    Details for 7 days backwards can be found here:
    https://heartrate-monitor.appspot.com/app/organizations/"""+str(org.key().id())+"""/report

    Check out the current state of your hearts at:
    https://heartrate-monitor.appspot.com/app/organizations/"""+str(org.key().id())+"""

    Kind regards
    https://heartrate-monitor.appspot.com/app/
    """

    try:
        message.send()
    except:
        print 'failed to send mail'
        pass





class ReportHandler(webapp2.RequestHandler):
       def get(self):
        rangestart = datetime.utcnow() - timedelta(days=7)
        organizations = Organization.all();
        for org in organizations:
            send_report(org, rangestart)
        self.response.out.write("ok")


app = webapp2.WSGIApplication([
    ('/sendreports.*', ReportHandler)
], debug=True)
