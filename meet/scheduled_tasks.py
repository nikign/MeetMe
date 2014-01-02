from meet.models import Meeting, RoomManager, Event
from meet.notification import inform_reservation, inform_no_room
from datetime import datetime
import pytz
from django.utils import timezone

every_hour_list = []

def every_hour(fn):
	every_hour_list.append(fn)
	return fn

@every_hour
def reserve_room_for_meetings():
	meeting_list = Meeting.objects.filter(status = Event.OPEN, confirmed = Meeting.NOT_SEEN)
	print meeting_list
	utc = pytz.UTC
	for meeting in meeting_list :
		try:
			if meeting.is_it_time_to_close(timezone.now()):
				meeting_reserve = RoomManager.reserve_room_for(meeting,timezone.now())
				inform_reservation(meeting_reserve)
		except Exception, e:
			meeting.cancel()
			inform_no_room(meeting)
