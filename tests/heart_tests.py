from models.heart import Heart, Flatline
from models.organization import Organization
import unittest
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from datetime import datetime

class HeartTestCase(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		org = Organization(title='Test')
		org.users = ['test@example.com']
		org.key = org.put()
		self.org = Organization.all().get()
	
	def tearDown(self):
		self.testbed.deactivate()

	def test_check_creates_flatline_for_configured(self):
		heart = self.org.get_heart('Test')
		heart.cron = "* * * * *"
		heart.threshold = 1

		flatlineBeforeCheck = heart.get_active_flatline()
		heart.check_flatLine()
		flatlineAfterCheck = heart.get_active_flatline()

		self.assertIsNone(flatlineBeforeCheck)
		self.assertIsNotNone(flatlineAfterCheck)

	def test_check_leaves_no_flatline_for_unconfigured(self):
		heart = self.org.get_heart('Test')
		heart.cron = ""
		heart.threshold = 1

		flatlineBeforeCheck = heart.get_active_flatline()
		heart.check_flatLine()
		flatlineAfterCheck = heart.get_active_flatline()

		self.assertIsNone(flatlineBeforeCheck)
		self.assertIsNone(flatlineAfterCheck)

	def test_check_leaves_no_flatline_for_deactivated(self):
		heart = self.org.get_heart('Test')
		heart.cron = "* * * * *"
		heart.threshold = 0

		flatlineBeforeCheck = heart.get_active_flatline()
		heart.check_flatLine()
		flatlineAfterCheck = heart.get_active_flatline()

		self.assertIsNone(flatlineBeforeCheck)
		self.assertIsNone(flatlineAfterCheck)

if __name__ == '__main__':
    unittest.main()