from django.test import TestCase
from meet.models import *
from datetime import datetime
import pytz

class MeetingTest(TestCase):
	fixtures = ['test_meeting.json', ]

	def test_how_many_voted(self):
		"""
		Tests that nimber of votes are calculated correctly.
		"""
		meetings = Meeting.objects
		meeting = meetings.get(pk= 1)
		self.assertEqual(meeting.__how_many_voted__(), 3)
		meeting = meetings.get(pk= 2)
		self.assertEqual(meeting.__how_many_voted__(), 1)

	def test_guest_count(self):
		"""
		Tests that nimber of votes are calculated correctly.
		"""
		meetings = Meeting.objects
		meeting = meetings.get(pk= 1)
		self.assertEqual(meeting.guest_count(), 3)
		meeting = meetings.get(pk= 2)
		self.assertEqual(meeting.guest_count(), 3)

	def test_is_it_time_to_close(self):
		"""
		Tests
		"""
		utc = pytz.UTC
		meetings = Meeting.objects
		meeting = meetings.get(pk= 1)
		self.assertTrue (meeting.is_it_time_to_close(datetime(2011, 5, 18, 21, 5, 53, 266396, utc)))
		self.assertTrue (meeting.is_it_time_to_close(datetime(2014, 5, 18, 21, 5, 53, 266396, utc)))
		meeting = meetings.get(pk= 2)
		self.assertTrue (meeting.is_it_time_to_close(datetime(2011, 5, 18, 21, 5, 53, 266396, utc)))
		self.assertFalse (meeting.is_it_time_to_close(datetime(2013, 4, 18, 21, 5, 53, 266396, utc)))




