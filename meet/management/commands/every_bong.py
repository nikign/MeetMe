from django.core.management.base import BaseCommand, CommandError
from meet.scheduled_tasks import every_hour_list

class Command(BaseCommand):
	help = 'Does all tasks that are Scheduled for one hour.'

	def handle(self, *args, **options):
		for fn in every_hour_list:
			fn()
