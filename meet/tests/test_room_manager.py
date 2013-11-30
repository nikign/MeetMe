from django.test import TestCase
from meet.models import *

class IntervalTest(TestCase):
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
		self.assertEqual(room.capacity, 11)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 11)
		self.assertEqual(room.capacity, 11)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 12)
		self.assertEqual(room.capacity, 30)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 13)
		self.assertEqual(room.capacity, 30)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 30)
		self.assertEqual(room.capacity, 30)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 31)
		self.assertEqual(room.capacity, 32)
		interval = intervals.get(pk=4)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 12)
		self.assertEqual(room.id, 3)
		
	def test_doesnt_find_room_because_rooms_are_full(self):
		"There is no room suitable in that time"
		interval = Interval.objects.get(pk= 2)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 1)
		self.assertIsNone(room)
	
	def test_doesnt_find_room_because_rooms_are_small(self):
		"There is no room large enough"
		interval = Interval.objects.get(pk= 4)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 50)
		self.assertIsNone(room)	

	def test_doesnt_find_room_because_rooms_are_all_small_or_full(self):
		"There is no room suitable in that time or they are small"
		interval = Interval.objects.get(pk= 7)
		room = RoomManager.find_best_room_for_interval_and_capacity(interval, 13)
		self.assertIsNone(room)	
		
		
