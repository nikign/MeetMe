from meet.models import Meeting, Reservation
from meet.notification import *
from meet.mail_and_notification import *
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
				admins = User.objects.filter(super_user = True).all() #TODO : FIX
				for admin in admins:
					notif = InformReservationNotification()
					notif.reservation = meeting_reserve
					notif.recipient = admin.e_mail
					notif.save()
				print "meeting waiting for admin verification, id = ",meeting.id
		except Exception, e:
			notif = InformNoRoomNotification()
			notif.meeting = meeting
			notif.save()
			print "meeting cancelled due to lack of suitable rooms, id = ",meeting.id

