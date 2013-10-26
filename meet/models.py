from django.db import models
from django.contrib.auth.models import User
from django.utils import dateformat
from meet.exceptions import RoomNotAvailableException

class Room (models.Model):
	name = models.CharField(max_length = 30)
	capacity = models.IntegerField()
	address = models.TextField()

	def is_suitable_for_interval(self, interval):
		reserves = self.resevation_list().filter(interval__date=interval.date);
		for reserve in reserves:
			if(reserve.has_interference(interval)):
				return False
		return True


class RoomManager(models.Model):
	
	@classmethod
	def find_best_room_for_interval_and_capacity(interval, capacity):
		fitting_rooms = Room.objects.filter(capacity__gte=capacity)
		fitting_rooms = sorted(fitting_rooms, key=lambda room: room.capacity)
		for room in fitting_rooms:
			if room.is_suitable_for_interval(interval):
				return room
		return None


class Event (models.Model):
	#TODO register meeting in event
	title = models.CharField(max_length=30)
	description = models.TextField()
	creator = models.ForeignKey(User)
	guest_list = models.ManyToManyField(User, null=True, blank=True, 
											db_table="guest_lists",
											 related_name="invitations")#TODO : doc.
	deadline = models.DateTimeField() #Time constrain

	def __unicode__(self):
		return self.title


class Interval (models.Model):
	date = models.DateField()
	start = models.TimeField()
	finish = models.TimeField()
	event = models.ForeignKey(Event, related_name="options_list")

	def __unicode__(self):
		return "On " + str(self.date) + " from " + dateformat.TimeFormat(self.start).P() +\
		 " to " + dateformat.TimeFormat(self.finish).P()

	def has_interference(self, other):
		return self.date == other.date and (
			(self.start > other.start and self.start < other.finish) or
			(self.finish > other.start and self.finish < other.finish)
		)
		
	def how_many_votes(self):
		return self.votes_list().count()
		
	def how_many_will_come(self):
		return self.votes_list().filter(state__in=[Vote.COMING, Vote.IF_HAD_TO]).count()

	def how_many_happy_to_come(self):
		return self.votes_list().filter(state_eq=Vote.COMING).count()


class Reservation(models.Model):
	interval = models.ForeignKey(Interval)
	room  = models.ForeignKey(Room, related_name="reservation_list")

	@classmethod
	def reserve_room_for(meeting):
		options = meeting.get_feasible_intervals_in_order()
		guest_count = meeting.get_guest_count()
		for option in options:
			room = RoomManager.find_best_room_for_interval_and_capacity(option, guest_count)
			if room != None : 
				reservation = Reservation()
				reservation.interval=option
				reservation.room=room
				reservation.save()
				return reservation
		raise RoomNotAvailableException()


class Meeting (Event):
	confirmed = models.BooleanField(default=False)
	
	EVERYONE = 'ev'
	HALF_AT_LEAST = 'hl'
	WITH_MAX_AVAILABLE = 'mx'
	HOLDING_CONDITIONS = (
		(EVERYONE, 'Everybody Should come'), 
		(HALF_AT_LEAST, 'At least half should come'), 
		(WITH_MAX_AVAILABLE, 'Choose the option with max people coming')
	)

	conditions = models.CharField(max_length=2, 
									choices=HOLDING_CONDITIONS,
									default=WITH_MAX_AVAILABLE)

	reservation = models.ForeignKey(Reservation, null=True, blank=True, default=None)
	
	def __guest_count__(self):
		return self.guest_list().count()

	def __how_many_voted__(self):
		sample_interval = self.options_list()[0]
		return sample_interval.how_many_votes()
		
		
	def get_feasible_intervals_in_order(self):
		intervals = self.options_list().order_by('-how_many_will_come', '-how_many_happy_to_come')
		guest_count = self.__guest_count__()
		if self.conditions == EVERYONE:
			return intervals.filter(how_many_will_come_gte=guest_count)
		if self.conditions == HALF_AT_LEAST:
			return intervals.filter(how_many_will_come_gte=guest_count/2)
		ans = intervals.filter(how_many_will_come_gt=0).all()
		return ans

	def is_it_time_to_close(self):
		if time.now >= self.deadline:
			return True
		return self.__how_many_voted__() == self.__guest_count__()


class Vote (models.Model):
	COMING = 'dc'
	IF_HAD_TO = 'ih'
	NOT_COMING = 'no'
	VOTE = (
		(COMING, 'Definitely coming'),
		(IF_HAD_TO, 'Only if I have to'),
		(NOT_COMING, 'No way')
	)
	state = models.CharField(max_length=2, 
							choices=VOTE)
	interval = models.ForeignKey(Interval, related_name="votes_list")
	voter = models.ForeignKey(User)


class Notification (models.Model):
	INVITED = 'in'
	BEING_HELD = 'bh'
	CANCELLED = 'ca'
	SOMEONE_VOTED = 'sv'
	ASK_CONFIRMATION = 'ac'
	NO_ROOM = 'nr'
	MESSAGE = (
		(INVITED, 'Invited'),
		(BEING_HELD, 'Being held'),
		(CANCELLED, 'Cancelled'),
		(SOMEONE_VOTED, 'Someone voted'),
		(ASK_CONFIRMATION, 'Meeting is being held an waiting for your confirmation.'),
		(NO_ROOM, 'No room is available in requested times, please ask for revote.'),
	)
	category = models.CharField(max_length=2, 
							choices=MESSAGE)
	event = models.ForeignKey(Event)	
	recepiant = models.ForeignKey(User)
	vote = models.ForeignKey(Vote)
