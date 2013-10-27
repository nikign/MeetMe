
from django.test import TestCase
from meet.models import *
from meet.exceptions import RoomNotAvailableException

class RoomTest(TestCase):
	fixtures = ['test_reservation.json', ]
	# TODO: use Interval Mock
	def test_suitable_room(self):
		"""
		Tests that checking if a room is suitable for an interval works correctly.
		"""
		meetings = Meeting.objects
		meeting_e_maryam_ina = meetings.get(pk=2)
		room_e_maryam = Reservation.reserve_room_for(meeting_e_maryam_ina)
		self.assertEqual(room_e_maryam.room.name, 'room403')
		meeting_e_ma = meetings.get(pk=3)
		with self.assertRaises(RoomNotAvailableException):
			room_e_ma = Reservation.reserve_room_for(meeting_e_ma)