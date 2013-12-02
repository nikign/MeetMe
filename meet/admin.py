from django.contrib import admin
from meet.models import *

class RoomAdmin(admin.ModelAdmin):
	fields = ['name','capacity','address']
	list_display = ('name', 'capacity')


class IntervalInline(admin.TabularInline):
	model = Interval


class EventAdmin(admin.ModelAdmin):
	fields = ['title', 'description', 'creator', 'guest_list', 'deadline', 'status']
	list_display = ('title', )
	inlines = [ IntervalInline ]


class MeetingAdmin(admin.ModelAdmin):
	fields = ['title', 'description', 'creator', 'guest_list', 'deadline', 'confirmed', 'reservation', 'status']
	inlines = [ IntervalInline ]

class VoteAdmin(admin.ModelAdmin):
	list_display = ('state', 'interval', 'voter')

class IntervalAdmin(admin.ModelAdmin):
	list_display = ('date', 'start', 'finish', 'event')

class ReservationAdmin(admin.ModelAdmin):
	list_display = ('interval_date', 'interval_from', 'interval_to', 'room')

	def interval_date(self, obj):
		return obj.interval.date
	interval_date.short_description = 'Date'

	def interval_from(self, obj):
		return obj.interval.start
	interval_from.short_description = 'From'

	def interval_to(self, obj):
		return obj.interval.finish
	interval_to.short_description = 'To'




admin.site.register(Interval, IntervalAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Notification)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(ClosingCondition)
for key in ClosingCondition.condition_keys:
	admin.site.register(ClosingCondition.key_to_type_map[key])

