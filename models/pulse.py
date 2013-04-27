from google.appengine.ext import db

class Pulse(db.Model):
	date = db.DateTimeProperty(auto_now_add=True)