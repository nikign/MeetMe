from django.test import TestCase
from meet.models import *
from datetime import datetime

class MeetingTest(TestCase):
	pass
	# fixtures = ['test_meeting.json', ]

	# def test_how_many_voted(self):
	# 	"""
	# 	Tests that nimber of votes are calculated correctly.
	# 	"""
	# 	meetings = Meeting.objects
	# 	meeting = meetings.get(pk= 2)
	# 	self.assertEqual(meeting.__how_many_voted__(), 7)
	# 	meeting = meetings.get(pk= 3)
	# 	self.assertEqual(meeting.__how_many_voted__(), 3)

	# def test_get_feasible_intervals_in_order(self):
	# 	"""
	# 	Tests 
	# 	"""
	# 	pass

	# def test_is_it_time_to_close(self):
	# 	"""
	# 	Tests
	# 	"""
	# 	meetings = Meeting.objects
	# 	meeting = meetings.get(pk= 2)
	# 	self.assertTrue (meeting.is_it_time_to_close(datetime(2011, 5, 18, 21, 5, 53, 266396)))
	# 	# meeting = meetings.get(pk= 3)
	# 	# self.assertTrue (meeting.is_it_time_to_close())

