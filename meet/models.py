from django.db import models
from django.contrib.auth.models import User
from django.utils import dateformat

class Room (models.Model):
	name = models.CharField(max_length = 30)
	capacity = models.IntegerField()
	address = models.TextField()


class Event (models.Model):
	#TODO register meeting in event
	title = models.CharField(max_length = 30)
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
		return "On "+str(self.date)+" from "+dateformat.TimeFormat(self.start).P()+ " to "+dateformat.TimeFormat(self.finish).P()


class Reservation(models.Model):
	interval = models.ForeignKey(Interval)
	room  = models.ForeignKey(Room)


class Meeting (Event):
	confirmed = models.BooleanField(default = False)
	
	EVERYONE = 'ev'
	HALF_AT_LEAST = 'hl'
	WITH_MAX_AVAILABLE = 'mx'
	HOLDING_CONDITIONS = (
		(EVERYONE, 'Everybody Should come'), 
		(HALF_AT_LEAST, 'At least half should come'), 
		(WITH_MAX_AVAILABLE, 'Choose the option with max people coming')
	)

	conditions = models.CharField(max_length=2, 
									choices = HOLDING_CONDITIONS,
									default = WITH_MAX_AVAILABLE)
	reservation = models.ForeignKey(Reservation, null=True, blank=True, default=None)


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
							choices = VOTE)
	interval = models.ForeignKey(Interval)
	voter = models.ForeignKey(User)


class Notification (models.Model):
	INVITED = 'in'
	BEING_HELD = 'bh'
	CANCELLED = 'ca'
	SOMEONE_VOTED = 'sv'
	MESSAGE = (
		(INVITED, 'Invited'),
		(BEING_HELD, 'Being held'),
		(CANCELLED, 'Cancelled'),
		(SOMEONE_VOTED, 'Someone voted'),
	)
	category = models.CharField(max_length=2, 
							choices = MESSAGE)
	event = models.ForeignKey(Event)
	
	recepiant = models.ForeignKey(User)
	vote = models.ForeignKey(Vote)



