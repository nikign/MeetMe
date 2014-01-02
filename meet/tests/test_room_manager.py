from django.test import TestCase
from meet.models import *
import datetime
import pytz
utc = pytz.UTC

class RoomManagerTest(TestCase):
	fixtures = ['test_room_manager.json', ]


	def test_finds_room(self):
		"This ones are supposed to find the room"		
		intervals = Interval.objects
		interval = intervals.get(pk=4)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 1)
		self.assertIsNotNone(room)
		interval = intervals.get(pk=7)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 1)
		self.assertIsNotNone(room)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 12)
		self.assertIsNotNone(room)

	def test_finds_best_room_for_capacity(self):
		"If selected room has enough capacity"
		intervals = Interval.objects
		interval = intervals.get(pk=4)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 1)
		self.assertEqual(room.capacity, 30)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 11)
		self.assertEqual(room.capacity, 30)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 12)
		self.assertEqual(room.capacity, 30)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 13)
		self.assertEqual(room.capacity, 30)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 30)
		self.assertEqual(room.capacity, 30)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 31)
		self.assertEqual(room.capacity, 50)
		# interval = intervals.get(pk=4)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 12)
		self.assertEqual(room.id, 1)
		
	def test_doesnt_find_room_because_rooms_are_full(self):
		"There is no room suitable in that time"
		interval = Interval.objects.get(pk= 1)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 1)
		self.assertIsNone(room)
	
	def test_doesnt_find_room_because_rooms_are_small(self):
		"There is no room large enough"
		interval = Interval.objects.get(pk= 4)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 51)
		self.assertIsNone(room)	

	def test_doesnt_find_room_because_rooms_are_all_small_or_full(self):
		"There is no room suitable in that time or they are small"
		interval = Interval.objects.get(pk= 7)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 33)
		self.assertIsNone(room)	
		
# class RoomManagerTest2(TestCase):
# 	fixtures = ['test_reservation.json', ]
	def test_reservation(self):
		"""
		Tests that reservation for a room performs well, whether room is available or not.
		"""
		meetings = Meeting.objects
		with self.assertRaises(RoomNotAvailableException):
			meeting = Meeting.objects.get(pk=1)
			room = RoomManager.reserve_room_for(meeting, 
				datetime.datetime(2014,12,2).replace(tzinfo=utc))
		meeting = Meeting.objects.get(pk=1)
		res = RoomManager.reserve_room_for(meeting, 
			datetime.datetime(2012,12,2).replace(tzinfo=utc))
		self.assertEqual(res.room.id , 1)

		# room available
		# reservation_before = Reservation.objects.all().count()
		# meeting_e_maryam_ina = meetings.get(pk=2)
		# room_e_maryam = RoomManager.reserve_room_for(meeting_e_maryam_ina)
		# self.assertEqual(room_e_maryam.room.name, 'room403')
		# self.assertEqual(Reservation.objects.all().count(), reservation_before + 1)
		# # room not available
		# meeting_e_ma = meetings.get(pk=3)
		# with self.assertRaises(RoomNotAvailableException):
		# 	room_e_ma = RoomManager.reserve_room_for(meeting_e_ma)
		# self.assertEqual(Reservation.objects.all().count(), reservation_before + 1)
		
