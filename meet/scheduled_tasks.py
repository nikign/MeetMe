from meet.models import Meeting, Reservation
from meet.mail_and_notification import *

every_hour_list = []

def every_hour(fn):
	every_hour_list.append(fn)
	return fn

@every_hour
def reserve_room_for_meetings():
	meeting_list = Meeting.objects.filter(status = Meeting.OPEN, confirmed = False)
	for meeting in meeting_list:
		try:
			meeting_reserve = Reservation.reserve_room_for(meeting)
			inform_admin_reservation(meeting_reserve)
			print "meeting waiting for admin verification, id = ",meeting.id
		except Exception, e:
			inform_no_room_to_owner(meeting)
			print "meeting cancelled due to lack of suitable rooms, id = ",meeting.id

