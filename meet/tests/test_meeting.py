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
		self.assertEqual(meeting.__how_many_voted__(), 3)

	def test_guest_count(self):
		"""
		Tests that nimber of votes are calculated correctly.
		"""
		meetings = Meeting.objects
		meeting = meetings.get(pk= 1)
		self.assertEqual(meeting.guest_count(), 3)
		meeting = meetings.get(pk= 2)
		self.assertEqual(meeting.guest_count(), 4)

	def test_is_it_time_to_close(self):
		"""
		Tests if correct decision is made anout time of clising meeting
		"""
		utc = pytz.UTC
		meetings = Meeting.objects
		meeting = meetings.get(pk= 1)
		self.assertTrue (meeting.is_it_time_to_close(datetime(2011, 5, 18, 21, 5, 53, 266396, utc)))
		self.assertTrue (meeting.is_it_time_to_close(datetime(2014, 5, 18, 21, 5, 53, 266396, utc)))
		meeting = meetings.get(pk= 2)
		self.assertTrue (meeting.is_it_time_to_close(datetime(2011, 5, 18, 21, 5, 53, 266396, utc)))
		self.assertFalse (meeting.is_it_time_to_close(datetime(2013, 4, 18, 21, 5, 53, 266396, utc)))

	def test_how_get_feasible_intervals_in_order(self):
		"""
		Tests that nimber of votes are calculated correctly.
		"""
		meetings = Meeting.objects

		meeting = meetings.get(pk= 1)
		res = meeting.get_feasible_intervals_in_order()
		self.assertEqual (len(res) , 3)
		self.assertEqual (res[0].how_many_will_come() , 2)
		self.assertEqual (res[1].how_many_will_come() , 1)
		self.assertEqual (res[2].how_many_will_come() , 1)

		meeting = meetings.get(pk= 2)
		res = meeting.get_feasible_intervals_in_order()
		self.assertEqual (len(res) , 3)
		self.assertEqual (res[0].how_many_will_come() , 2)
		self.assertEqual (res[1].how_many_will_come() , 2)
		self.assertEqual (res[2].how_many_will_come() , 2)

		meeting = meetings.get(pk= 5)
		res = meeting.get_feasible_intervals_in_order()
		self.assertEqual (len(res) , 1)


	def test_confirm(self):
		"""
		A brief test on meeting::confirm 
		"""
		meetings = Meeting.objects
		meeting = meetings.get(pk= 1)
		meeting.confirm()
		self.assertEqual (meeting.confirmed , Meeting.CONFIRMED)
	
	def test_cancel(self):
		"""
		A brief test on meeting::cancel 
		"""
		meetings = Meeting.objects
		meeting = meetings.get(pk= 2)
		meeting.cancel()
		self.assertEqual (meeting.confirmed , Meeting.CANCELLED)

		



