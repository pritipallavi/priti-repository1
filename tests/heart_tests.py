from models.heart import Heart, Flatline
from models.organization import Organization
import unittest
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from datetime import datetime, timedelta
from pytz.gae import pytz

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
		heart.last_pulse = datetime( 1980, 5, 4, 15, 40 )
		heart.threshold = 1

		flatlineBeforeCheck = heart.get_active_flatline()
		heart.check_flatLine()
		flatlineAfterCheck = heart.get_active_flatline()

		self.assertIsNone(flatlineBeforeCheck)
		self.assertIsNotNone(flatlineAfterCheck)

	def test_check_creates_no_flatline_for_configured_without_last_pulse(self):
		heart = self.org.get_heart('Test')
		heart.cron = "* * * * *"
		heart.threshold = 1

		flatlineBeforeCheck = heart.get_active_flatline()
		heart.check_flatLine()
		flatlineAfterCheck = heart.get_active_flatline()

		self.assertIsNone(flatlineBeforeCheck)
		self.assertIsNone(flatlineAfterCheck)

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

	def test_is_not_flatlined_having_no_pulse_within_one_day_and_one_day_threshold(self):
		heart = self.org.get_heart('Test')
		heart.last_pulse = datetime.now() - timedelta(days=1, minutes=1)
		heart.cron = heart.last_pulse.strftime( "%M %H" ) + " * * *"
		heart.threshold = int(timedelta(days=1).total_seconds())

		self.assertFalse(heart.is_flatlined())

	def test_is_not_flatlined_when_1day_threshold_makes_next_date_overlap(self):
		heart = self.org.get_heart('Test')
		heart.last_pulse = datetime.now() - timedelta(days=2, minutes=1)
		heart.cron = heart.last_pulse.strftime( "%M %H" ) + " * * *"
		heart.threshold = int(timedelta(days=1).total_seconds())

		self.assertFalse(heart.is_flatlined())

	def test_is_not_flatlined_when_2h_threshold_makes_next_date_overlap(self):
		heart = self.org.get_heart('Test')
		heart.last_pulse = datetime.now() - timedelta(hours=2, minutes=1)
		heart.cron = "0 * * * *"
		heart.threshold = int(timedelta(hours=1).total_seconds())

		self.assertFalse(heart.is_flatlined())

	def test_next_expected_pulse_for_daily_midnight_schedule_is_next_midnight(self):
		heart = self.org.get_heart('Test')
		heart.last_pulse = datetime(1980, 5, 4, 15, 40)
		heart.cron = "0 0 * * *"

		(next_date, next_next_date) = heart.get_next_local_pulse_dates()
		self.assertEqual( pytz.utc.localize( datetime( 1980, 5, 5, 0, 0 ) ), next_date )
		self.assertEqual( pytz.utc.localize( datetime( 1980, 5, 6, 0, 0 ) ), next_next_date )

	def test_next_expected_pulse_for_every_hour_schedule_is_next_hour(self):
		heart = self.org.get_heart('Test')
		heart.last_pulse = datetime(1980, 5, 4, 15, 40)
		heart.cron = "0 * * * *"

		(next_date, next_next_date) = heart.get_next_local_pulse_dates()
		self.assertEqual( pytz.utc.localize( datetime( 1980, 5, 4, 16, 0 ) ), next_date )
		self.assertEqual( pytz.utc.localize( datetime( 1980, 5, 4, 17, 0 ) ), next_next_date )

	def test_next_expected_pulse_returns_localized_with_heart_tz(self):
		us_eastern = pytz.timezone("US/Eastern")
		local_last_pulse   = us_eastern.localize( datetime( 1980, 5, 4, 15, 40 ) )
		expected_next      = us_eastern.localize( datetime( 1980, 5, 4, 16, 0  ) )
		expected_next_next = us_eastern.localize( datetime( 1980, 5, 4, 17, 0  ) )

		heart = self.org.get_heart('Test')
		heart.last_pulse = local_last_pulse.astimezone(pytz.utc)
		heart.cron = "0 * * * *"
		heart.time_zone = "US/Eastern"

		(next_date, next_next_date) = heart.get_next_local_pulse_dates()

		self.assertEqual( expected_next, next_date )
		self.assertEqual( expected_next_next, next_next_date )

	def test_calculate_flatline_with_every_hour_schedule_1h_overlapping_threshold(self):
		us_eastern = pytz.timezone("US/Eastern")
		local_last_pulse  = us_eastern.localize( datetime( 1980, 5, 4, 15, 40 ) )
		# next pulse should be at 16:00 and flatline at 17:00, but will flatline at 18:00 due 
		# to a threshold that overlaps the periodicity of the cron schedule
		expected_flatline = us_eastern.localize( datetime( 1980, 5, 4, 18, 0  ) ) + timedelta(microseconds=1)

		heart = self.org.get_heart('Test')
		heart.last_pulse = local_last_pulse.astimezone(pytz.utc)
		heart.cron = "0 * * * *"
		heart.threshold = int(timedelta(hours=1).total_seconds())
		heart.time_zone = "US/Eastern"

		next_flatline = heart.calculate_next_flatline()

		self.assertEqual( expected_flatline, next_flatline )
		# self check
		utcnow = expected_flatline.astimezone(pytz.utc)
		self.assertTrue( heart.is_flatlined( utcnow ) )

	def test_calculate_flatline_with_every_5min_schedule_30min_threshold(self):
		heart = self.org.get_heart('Test')
		heart.cron = "*/5 * * * *"
		heart.threshold = int(timedelta(minutes=30).total_seconds())
		heart.timezone = "UTC"
		# last pulse 15:38; next pulse expected at 15:45 + 30 min threshold = flatlines after 16:15
		heart.last_pulse = datetime(1980, 5, 4, 15, 38)
		expected_flatline = pytz.utc.localize( datetime( 1980, 5, 4, 16, 15 ) + timedelta(microseconds=1) )

		next_flatline = heart.calculate_next_flatline()

		self.assertEqual( expected_flatline, next_flatline )
		# self check
		utcnow = expected_flatline.astimezone(pytz.utc)
		self.assertTrue( heart.is_flatlined( utcnow ) )


if __name__ == '__main__':
    unittest.main()