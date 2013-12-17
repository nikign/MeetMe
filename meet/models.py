from django.db import models
from django.contrib.auth.models import User
from django.utils import dateformat
from meet.exceptions import RoomNotAvailableException
from datetime import datetime
from model_utils.managers import InheritanceManager
from django.db.models import Q

class Room (models.Model):
	name = models.CharField(max_length = 30)
	capacity = models.IntegerField()
	address = models.TextField()

	def __unicode__(self):
		return '['+str(self.capacity)+'] '+self.name

	def is_suitable_for_interval(self, interval):
		reserves = self.reservation_list.filter(interval__date=interval.date);
		for reserve in reserves:
			if(reserve.interval.has_interference(interval)):
				return False

		return True


class RoomManager(models.Model):
	
	@classmethod
	def find_best_room_for_interval_and_capacity(cls, interval, capacity):
		fitting_rooms = Room.objects.filter(capacity__gte=capacity).order_by('capacity')
		for room in fitting_rooms:
			if room.is_suitable_for_interval(interval):
				return room
		return None

	@classmethod
	def reserve_room_for(cl, meeting):
		options = meeting.get_feasible_intervals_in_order()
		guest_count = meeting.guest_count()
		for option in options:
			room = RoomManager.find_best_room_for_interval_and_capacity(option, guest_count)
			if room != None :
				reservation = Reservation()
				reservation.interval=option
				reservation.room=room
				reservation.save()
				meeting.make_closed(reservation)
				return reservation
		raise RoomNotAvailableException()

class Event (models.Model):
	#TODO register meeting in event

	OPEN = 'op'
	CLOSED = 'cl'

	STATUS = (
		(OPEN, 'Open'),
		(CLOSED, 'Closed'),
	)

	title = models.CharField(max_length=30)
	description = models.TextField()
	creator = models.ForeignKey(User)
	guest_list = models.ManyToManyField(User, null=True, blank=True, 
											db_table="guest_lists",
											 related_name="invitations")#TODO : doc.
	deadline = models.DateTimeField() #Time constrain
	status = models.CharField(max_length=2, 
									choices=STATUS,
									default=OPEN,
	)

	def __unicode__(self):
		return self.title

	def has_user_voted(self,user):
		return Vote.objects.filter(voter=user,interval__event=self).count()>0

	def get_guest_emails(self):
		email_list = [user.e_mail for user in self.guest_list]
		return email_list

	def get_creator_email(self):
		return self.creator.e_mail


class Interval (models.Model):
	date = models.DateField()
	start = models.TimeField()
	finish = models.TimeField()
	event = models.ForeignKey(Event, related_name="options_list")

	def __unicode__(self):
		return "On " + str(self.date) + " from " + dateformat.TimeFormat(self.start).P() +\
		 " to " + dateformat.TimeFormat(self.finish).P() + "for event" + self.event.title

	def has_interference(self, other):
		return self.date == other.date and (
			(self.start >= other.start and self.start < other.finish) or
			(self.finish > other.start and self.finish <= other.finish)
		)
		
	def how_many_votes(self):
		return self.votes_list.count()
		
	def how_many_will_come(self):
		return self.votes_list.filter(state__in=[Vote.COMING, Vote.IF_HAD_TO]).count()

	def how_many_happy_to_come(self):
		return self.votes_list.filter(state=Vote.COMING).count()

	def is_guest_coming(self, user):
		return self.votes_list.filter(voter=user, state__in=[Vote.COMING, Vote.IF_HAD_TO]).count()>0
		
	def get_coming_list(self):
		return self.votes_list.filter( state__in=[Vote.COMING, Vote.IF_HAD_TO])

	def get_vote(self, user):
		return Vote.objects.filter(voter=user, interval=self)

class Reservation(models.Model):
	interval = models.ForeignKey(Interval)
	room  = models.ForeignKey(Room, related_name="reservation_list")

class Meeting (Event):

	NOT_SEEN = 'ns'
	CONFIRMED = 'cn'
	CANCELLED = 'cc'

	CONFIRMATION = (
		(NOT_SEEN, 'Not seen yet'),
		(CONFIRMED, 'Confirmed'),
		(CANCELLED, 'Cancelled'),
	)

	# confirmed = models.BooleanField(default=False)
	confirmed = models.CharField(max_length=2, 
									choices=CONFIRMATION,
									default=NOT_SEEN)

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
	
	def guest_count(self):
		return self.guest_list.count()

	def __how_many_voted__(self):
		return Vote.objects.filter(interval__event=self).values('voter').distinct().count()
		
	def get_feasible_intervals_in_order(self):
		closing_condition = ClosingCondition.objects.get_subclass(meeting=self)
		return closing_condition.get_feasible_intervals_in_order()

	def is_it_time_to_close(self, now_time):
		if self.deadline >= now_time:
			return True
		return self.__how_many_voted__() == self.guest_count()

	def make_closed(self, reservation):
		self.status = Event.CLOSED
		self.confirmed = Meeting.NOT_SEEN
		self.reservation = reservation
		self.save()

	def confirm(self):
		self.confirmed = Meeting.CONFIRMED
		self.save()

	def cancel(self):
		self.confirmed = Meeting.CANCELLED
		self.save()

	@classmethod
	def get_waiting_for_admin_meetings(cls):
		meetings = Meeting.objects.filter(status=Event.CLOSED, confirmed=Meeting.NOT_SEEN)
		return meetings


class ClosingCondition(models.Model):
	# key = 'abs'
	# description = "there shouldn't be any instance of this"
	condition_keys = []
	key_to_type_map = {}
	key_to_description_map = {}

	objects = InheritanceManager()

	meeting = models.OneToOneField(Meeting, primary_key=True, related_name='closing_condition')


	def get_feasible_intervals_in_order(self):
		print "injaaaaaaa"
		raise NotImplementedError("error message")

	# def __init__(self, options_list, guest_list):
	# 	self.options_list = options_list
	# 	self.guest_list = guest_list

	# def __guest_count__(self):
	# 	return self.guest_list.count()

	@classmethod
	def register(cls, subclass):
		cls.condition_keys.append(subclass.key)
		cls.key_to_type_map[subclass.key] = subclass
		cls.key_to_description_map[subclass.key] = subclass.description
		return subclass

	# def is_ev(self):
	# 	return hasattr(self, 'everyoneclosingcondition') and self.everyoneclosingcondition is not None
	
	# def is_hl(self):
	# 	return hasattr(self, 'everyoneclosingcondition') and self.everyoneclosingcondition is not None
	
	# def is_hl(self):
	# 	return hasattr(self, 'everyoneclosingcondition') and self.everyoneclosingcondition is not None


@ClosingCondition.register
class EveryoneClosingCondition(ClosingCondition):
	key = 'ev'
	description = 'Everybody Should come'

	def get_feasible_intervals_in_order(self):
		guest_count = self.meeting.guest_list.count()
		intervals = self.meeting.options_list.filter(votes_list__state__in=[Vote.COMING, Vote.IF_HAD_TO])
		intervals_list = list(intervals.all())
		intervals_list.sort(key=lambda x: (x.how_many_will_come(), x.how_many_happy_to_come()) , reverse=True)
		return intervals_list or []


@ClosingCondition.register
class HalfAtLeastClosingCondition(ClosingCondition):
	key = 'hl'
	description = 'At least half should come'

	def get_feasible_intervals_in_order(self):
		guest_count = self.meeting.guest_list.count()
		intervals = list(self.meeting.options_list.all())
		intervals.sort(key=lambda x: (x.how_many_will_come(), x.how_many_happy_to_come()) , reverse=True)
		return intervals.filter(votes_list__state__in=[Vote.COMING, Vote.IF_HAD_TO]).count()>=guest_count/2


@ClosingCondition.register
class MaxAvailableClosingCondition(ClosingCondition):
	key = 'mx'
	description = 'Choose the option with max people coming'

	def get_feasible_intervals_in_order(self):
		guest_count = self.meeting.guest_list.count()
		
		intervals = list(self.meeting.options_list.all())
		intervals.sort(key=lambda x: (x.how_many_will_come(), x.how_many_happy_to_come()) , reverse=True)
		return intervals or []


@ClosingCondition.register
class AdvancedClosingCondition(ClosingCondition):
	key = 'ad'
	description = 'Use advanced options'

	must_come_list = models.ManyToManyField(User, null=True, blank=True, 
											db_table="must_come_guest_list",
											 related_name="must_go_events")

	def get_feasible_intervals_in_order(self):
		intervals = list(self.meeting.options_list.filter().all())
		feasibles= []
		for interval in intervals:
			for guest in self.must_come_list.all():
				if not interval.is_guest_coming(guest):
					break
			else:
				feasibles.append(interval)
		feasibles.sort(key=lambda x: (x.how_many_will_come(), x.how_many_happy_to_come()) , reverse=True)
		return feasibles


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

	def update_state(self, new_state):
		self.state = new_state
		self.save()


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
	vote = models.ForeignKey(Vote, null = True, blank= True)


#METHODS TO ADD TO USER
def user_events(self, fr, to):
	return Event.objects.filter(Q(creator=self)|Q(guest_list=self)).order_by('-deadline').distinct()[fr:to].all()

def is_invited_to(self, event):
	return event.creator==self or self in event.guest_list.all()

User.add_to_class('related_events', user_events)
User.add_to_class('is_invited_to', is_invited_to)
