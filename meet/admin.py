from django.contrib import admin
from meet.models import *

class RoomAdmin(admin.ModelAdmin):
	fields = ['name','capacity','address']
	list_display = ('name', 'capacity')

class IntervalInline(admin.TabularInline):
	model = Interval


class EventAdmin(admin.ModelAdmin):
	fields= ['title', 'description', 'creator', 'guest_list']
	inlines = [ IntervalInline ]

class MeetingAdmin(admin.ModelAdmin):
	fields= ['title', 'description', 'creator', 'guest_list', 'confirmed', 'conditions','reservation']
	inlines = [ IntervalInline ]



admin.site.register(Interval)
admin.site.register(Room, RoomAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Vote)
admin.site.register(Notification)
admin.site.register(Reservation)
