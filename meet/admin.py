from django.contrib import admin
from meet.models import *

class RoomAdmin(admin.ModelAdmin):
	fields = ['name','capacity','address']
	list_display = ('name', 'capacity')

admin.site.register(Room, RoomAdmin)
admin.site.register(Event)
admin.site.register(Meeting)
admin.site.register(Interval)
admin.site.register(Vote)
admin.site.register(Notification)
admin.site.register(Reservation)
