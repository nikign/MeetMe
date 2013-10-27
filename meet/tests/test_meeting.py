from django.test import TestCase
from meet.models import *

class MeetingTest(TestCase):
	fixtures = ['test_meeting.json', ]

	def test_how_many_voted(self):
		"""
		Tests that Interval inference is checked correctly.
		"""
		# meetings = Meeting.objects
		# meeting = meetings.get(pk= 2)
		# self.assertEqual(meeting.__how_many_voted__(), 0)
		# meeting = meetings.get(pk= 3)
		# self.assertEqual(meeting.__how_many_voted__(), 2)

	def test_get_feasible_intervals_in_order(self):
		"""
		Tests 
		"""
		pass

	def test_is_it_time_to_close(self):
		"""
		Tests
		"""
		# meetings = Meeting.objects
		# meeting = meetings.get(pk= 2)
		# self.assertTrue (meeting.is_it_time_to_close())
		# meeting = meetings.get(pk= 3)
		# self.assertTrue (meeting.is_it_time_to_close())


		