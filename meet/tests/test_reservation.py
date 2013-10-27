
from django.test import TestCase
from meet.models import *
from meet.exceptions import RoomNotAvailableException

class RoomTest(TestCase):
	fixtures = ['test_reservation.json', ]
	def test_reservation(self):
		"""
		Tests that reservation for a room performs well, whether room is available or not.
		"""
		meetings = Meeting.objects
		# room available
		meeting_e_maryam_ina = meetings.get(pk=2)
		room_e_maryam = Reservation.reserve_room_for(meeting_e_maryam_ina)
		self.assertEqual(room_e_maryam.room.name, 'room403')
		# room not available
		meeting_e_ma = meetings.get(pk=3)
		with self.assertRaises(RoomNotAvailableException):
			room_e_ma = Reservation.reserve_room_for(meeting_e_ma)