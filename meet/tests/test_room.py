
from django.test import TestCase
from meet.models import *

class RoomTest(TestCase):
	fixtures = ['test_room.json', ]
	# TODO: use Interval Mock
	def test_suitable_room(self):
		"""
		Tests that checking if a room is suitable for an interval works correctly.
		"""
		rooms = Room.objects.all()
		intervals = Interval.objects.all()
		self.assertEqual(rooms[0].is_suitable_for_interval(intervals[2]), True)
		self.assertEqual(rooms[0].is_suitable_for_interval(intervals[3]), False)
		self.assertEqual(rooms[1].is_suitable_for_interval(intervals[0]), True)
		self.assertEqual(rooms[1].is_suitable_for_interval(intervals[1]), True)
		self.assertEqual(rooms[1].is_suitable_for_interval(intervals[2]), True)
		self.assertEqual(rooms[1].is_suitable_for_interval(intervals[3]), True)
