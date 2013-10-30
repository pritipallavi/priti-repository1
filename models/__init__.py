from google.appengine.api import mail
from lib.pubnub import pubnub


def resuscitate_mail(heart):
    message = mail.EmailMessage(sender="alerts@heartrate-monitor.appspotmail.com",
                                subject=heart.title + " has a pulse again")

    org = heart.parent()
    if org.alert_email is '' or org.alert_email is None:
        message.to = map(lambda user: user, heart.parent().users)
    else:
        message.to = org.alert_email
    message.body = """
    Good news!

    The heart """+heart.title+""" has started to beat again.

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

    try:
        pub = pubnub.Pubnub(
            'publish key',
            'subscription key',
            'secret',
            False)
        pub.publish({
            'channel': 'remotex-alerts',
            'message': {
                'heart': heart.key().name(),
                'flatline': 'resuscitated'
            }
        })
    except:
        print ' failed to send to pubnub'
        pass


def flatline_mail(heart):
    message = mail.EmailMessage(sender="alerts@heartrate-monitor.appspotmail.com",
                                subject=heart.title + " has flatlined")

    org = heart.parent()
    if org.alert_email is '' or org.alert_email is None:
        message.to = map(lambda user: user, heart.parent().users)
    else:
        message.to = org.alert_email

    message.body = """
    Bad news!

    The heart """+heart.title+""" has not had a pulse within its threshold.

    The last pulse recieved was at """+str(heart.last_pulse)+"""

    See the heart at:
    https://heartrate-monitor.appspot.com/app/organizations/"""+str(heart.parent().key().id())+"""/hearts/"""+heart.key().name()+"""

    Check out the current state of your hearts at:
    https://heartrate-monitor.appspot.com/app/organizations/"""+str(heart.parent().key().id())+"""

    Kind regards
    https://heartrate-monitor.appspot.com/app/
    """
    try:
        message.send()
    except:
        print 'failed to send mail'
        pass
    try:
        pub = pubnub.Pubnub(
            "pub-c-1f0c3356-d4c4-42ac-a84e-27d39e781b85",
            "sub-c-c8c9e356-df06-11e2-95e6-02ee2ddab7fe",
            'sec-c-ZTAyYTY2ZDItNzY2ZS00YmMzLTk0MjItNTk1ODRjZjU3ZTY2',
            False)
        pub.publish({
            'channel': 'remotex-alerts',
            'message': {
                'heart': heart.key().name(),
                'start': str(heart.last_pulse),
                'title': heart.title,
                'flatline': 'flatline'
            }
        })
    except:
        print 'failed to send to pubnub'
        pass


def invite_mail(invitation):
    message = mail.EmailMessage(sender="invite@heartrate-monitor.appspotmail.com",
                                subject="Invitation to "+invitation.parent().title)

    message.to = invitation.email
    message.body = """
    Hi!

    You have been invited to """+invitation.parent().title+""".

    Heartrate-monitor will keep track of scheduled tasks reporting to it. Informing you when the tasks stop reporting in within the expected time.
    Simple yet effective way to keep track that tasks are being executed.

    Respond to this invitation at:
    https://heartrate-monitor.appspot.com/app/invitations/"""+str(invitation.key())+"""


    Kind regards
    https://heartrate-monitor.appspot.com/app/
    """

    try:
        message.send()
    except:
        print 'failed to send mail'
        pass
