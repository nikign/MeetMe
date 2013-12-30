from meet.models import Meeting, Reservation
from meet.notification import inform_reservation, inform_no_room
from datetime import datetime
import pytz

every_hour_list = []

def every_hour(fn):
	every_hour_list.append(fn)
	return fn

@every_hour
def reserve_room_for_meetings():
	meeting_list = Meeting.objects.filter(status = Meeting.OPEN, confirmed = False)
	utc = pytz.UTC
	for meeting in meeting_list :
		try:
			if meeting.is_it_time_to_close(datetime.now.replace(tzinfo=utc)):
				meeting_reserve = RoomManager.reserve_room_for(meeting)
				inform_reservation(meeting_reserve)
		except Exception, e:
			inform_no_room(meeting)
