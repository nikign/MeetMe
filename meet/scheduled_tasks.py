from meet.models import Meeting
from meet.mail_and_notification

#run every 1 hour
def reserve_room_for_meetings():
	#for every being closed meeting:
	meeting_reserve = meeting.find_and_reserve_best_fitting_time()
	if meeting_reserve:
		inform_admin_reservation(meeting_reserve)

