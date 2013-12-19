from django.test import TestCase
from meet.models import *
from django.core.exceptions import *

class IntervalTest(TestCase):
	fixtures = ['test_interval.json', ]
	def test_interference(self):
		"""
		Tests that Interval inference is checked correctly.
		"""
		intervals = Interval.objects.all()

		msg_beginning_the_same = 'Assertion failes for intervals whose beginnings are equal.'
		self.assertEqual(intervals[4].has_interference(intervals[0]), True, msg_beginning_the_same)

		msg_usual_interference_true = "Even usual interference isn't working, when interference!"
		self.assertEqual(intervals[0].has_interference(intervals[1]), True, msg_usual_interference_true)
		
		msg_usual_interference_false = "Even usual interference isn't working, when no interference!"
		self.assertEqual(intervals[0].has_interference(intervals[2]), False, msg_usual_interference_false)
		self.assertEqual(intervals[1].has_interference(intervals[2]), False, msg_usual_interference_false)
		self.assertEqual(intervals[2].has_interference(intervals[3]), False, msg_usual_interference_false)
		self.assertEqual(intervals[4].has_interference(intervals[2]), False, msg_usual_interference_false)
		self.assertEqual(intervals[4].has_interference(intervals[3]), False, msg_usual_interference_false)
		
		msg_beginning_on_end = 'When beginning equals to end says interference!'
		self.assertEqual(intervals[0].has_interference(intervals[3]), False, msg_beginning_on_end)
		self.assertEqual(intervals[4].has_interference(intervals[1]), False, msg_beginning_on_end)

		msg_ends_the_same = 'Assertion failes for intervals whose ends are equal.'
		self.assertEqual(intervals[1].has_interference(intervals[3]), True, msg_ends_the_same)
		


	def test_how_many_votes(self):
		"""
		Tests vote count to be correct
		"""
		intervals = Interval.objects.all()
		self.assertEqual(intervals[0].how_many_votes(), 3)
		self.assertEqual(intervals[1].how_many_votes(), 0)
		self.assertEqual(intervals[2].how_many_votes(), 0)
		self.assertEqual(intervals[3].how_many_votes(), 0)
		self.assertEqual(intervals[4].how_many_votes(), 0)
	
	def test_how_many_will_come(self):
		"""
		Tests 'coming' and 'if I have to' vote count to be correct
		"""
		intervals = Interval.objects.all()
		self.assertEqual(intervals[0].how_many_will_come(), 2)
		self.assertEqual(intervals[1].how_many_will_come(), 0)
		self.assertEqual(intervals[2].how_many_will_come(), 0)
		self.assertEqual(intervals[3].how_many_will_come(), 0)
		self.assertEqual(intervals[4].how_many_will_come(), 0)
	
	def test_how_many_happy_to_come(self):
		"""
		Tests 'coming' vote count to be correct
		"""
		intervals = Interval.objects.all()
		self.assertEqual(intervals[0].how_many_happy_to_come(), 1)
		self.assertEqual(intervals[1].how_many_happy_to_come(), 0)
		self.assertEqual(intervals[2].how_many_happy_to_come(), 0)
		self.assertEqual(intervals[3].how_many_happy_to_come(), 0)
		self.assertEqual(intervals[4].how_many_happy_to_come(), 0)

	def test_is_guest_coming(self):
		"""
		Tests if a user voted "coming" or "if i had to" to a particular interval
		"""
		intervals = Interval.objects
		users = User.objects
		self.assertTrue(intervals.get(pk=2).is_guest_coming(users.get(pk=2)))
		self.assertTrue(intervals.get(pk=2).is_guest_coming(users.get(pk=3)))
		self.assertFalse(intervals.get(pk=2).is_guest_coming(users.get(pk=1)))
		self.assertFalse(intervals.get(pk=3).is_guest_coming(users.get(pk=1)))

	def test_get_vote(self):
		"""
		Tests if a user voted "coming" or "if i had to" to a particular interval
		"""
		intervals = Interval.objects
		users = User.objects
		vote = intervals.get(pk=2).get_vote(users.get(pk=2))
		self.assertEqual (vote.state , Vote.COMING)
		vote = intervals.get(pk=2).get_vote(users.get(pk=1))
		self.assertEqual (vote.state , Vote.NOT_COMING)
		vote = intervals.get(pk=2).get_vote(users.get(pk=3))
		self.assertEqual (vote.state , Vote.IF_HAD_TO)
		with self.assertRaises(ObjectDoesNotExist):
			vote = intervals.get(pk=3).get_vote(users.get(pk=3))
		


	def test_get_coming_list(self):
		"""
		Test if an interval returns its coming list correct
		"""
		intervals = Interval.objects
		cl = intervals.get(pk=2).get_coming_list()
		users = User.objects
		cl = [vote.voter for vote in cl]
		self.assertEqual(len(cl), 2)
		self.assertFalse (users.get(pk=1) in cl)
		self.assertTrue (users.get(pk=2) in cl)
		self.assertTrue (users.get(pk=3) in cl)
		cl = intervals.get(pk=3).get_coming_list()
		self.assertEqual(len(cl), 0)
		cl = intervals.get(pk=5).get_coming_list()
		self.assertEqual(len(cl), 0)
		

