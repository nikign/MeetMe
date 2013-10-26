from meet.models import Meeting
from meet.mail_and_notification

#run every 1 hour
def reserve_room_for_meetings():
	#for every being closed meeting:
	try:
		meeting_reserve = meeting.find_and_reserve_best_fitting_time()
		inform_admin_reservation(meeting_reserve)
	except Exception, e:
		pass
		#inform the creator

