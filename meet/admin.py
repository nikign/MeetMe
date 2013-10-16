from django.contrib import admin
from meet.models import *

class RoomAdmin(admin.ModelAdmin):
	fields = ['name','capacity','address']
	list_display = ('name', 'capacity')


class IntervalInline(admin.TabularInline):
	model = Interval


class EventAdmin(admin.ModelAdmin):
	fields = ['title', 'description', 'creator', 'guest_list']
	list_display = ('title', )
	inlines = [ IntervalInline ]


class MeetingAdmin(admin.ModelAdmin):
	fields = ['title', 'description', 'creator', 'guest_list', 'confirmed', 'conditions','reservation']
	inlines = [ IntervalInline ]

class VoteAdmin(admin.ModelAdmin):
	list_display = ('state', 'interval', 'voter')

class IntervalAdmin(admin.ModelAdmin):
	list_display = ('date', 'start', 'finish', 'event')


admin.site.register(Interval, IntervalAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Notification)
admin.site.register(Reservation)
