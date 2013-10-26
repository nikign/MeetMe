from meet.models import Meeting
from meet.mail_and_notification

#run every 1 hour
def reserve_room_for_meetings():
	meeting_list = Meeting.objects.filter(is_it_time_to_close_eq = True)
	for meeting in meeting_list:
		try:
			meeting_reserve = Reservation.reserve_room_for(meeting)
			inform_admin_reservation(meeting_reserve)
		except Exception, e:
			pass
			#inform the creator

