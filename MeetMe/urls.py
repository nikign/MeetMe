from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf.urls.defaults import handler404, handler500, handler403#, handler400
# from meet.views import create_wizard

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', 'meet.views.home', name='home'),
    # url(r'^MeetMe/', include('MeetMe.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^event/(?P<event_id>\d+)/vote' , 'meet.views.vote_event' , name='vote_event'),
    url(r'^event/(?P<event_id>\d+)/view' , 'meet.views.view_event' , name='view_event'),
    url(r'^meeting/(?P<meeting_id>\d+)/confirm/$', 'meet.views.confirm_meeting', name='confirm'),
    url(r'^meeting/(?P<meeting_id>\d+)/cancel/$', 'meet.views.cancel_meeting', name='cancel'),
    url(r'^admins/review/$' , 'meet.views.admin_review' , name='review'),
    url(r'^user/events/$' , 'meet.views.related_events' , name='related_events'),
    url(r'^event/vote' , 'meet.views.vote' , name='vote_save'),
    url(r'^create/', 'meet.views.create_wizard' , name='create'),
    url(r'^event/(?P<event_id>\d+)/edit/$', 'meet.views.edit_wizard' , name='edit'),
    url(r'^event/(?P<event_id>\d+)/revote/$', 'meet.views.revote' , name='revote'),
    url(r'^notif/(?P<notif_id>\d+)/mark_read/$', 'meet.views.mark_notif_read' , name='mark_notif_read'),

    url(r'^google/login/$', 'django_openid_auth.views.login_begin', name='openid-login'),
    url(r'^google/login-complete/$', 'django_openid_auth.views.login_complete', name='openid-complete'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/',}, name='logout'),
    url(r'^tzset/$', 'meet.views.set_timezone' , name='set_timezone'),
    

    # url(r'^fakelogin/', 'meet.test_utils.views.fake_login' , name='fake_login'),
)
handler404 = "meet.views.handler404"
handler500 = "meet.views.handler500"
handler403 = "meet.views.handler403"
handler400 = "meet.views.handler400"