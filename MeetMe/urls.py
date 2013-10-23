from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from meet.views import create_wizard
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
    url(r'^event/(?P<event_id>\d+)/view' , 'meet.views.view' , name='view'),
    url(r'^event/vote' , 'meet.views.vote' , name='vote'),
    url(r'^create2/', 'meet.views.create' , name='create'),
    url(r'^save_event/', 'meet.views.save_event' , name='save_event'),
    url(r'^google/login/$', 'django_openid_auth.views.login_begin', name='openid-login'),
    url(r'^google/login-complete/$', 'django_openid_auth.views.login_complete', name='openid-complete'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/',}, name='logout'),

    url(r'^saved/', 'meet.views.event_saved' , name='event_saved'),
    url(r'^create/', create_wizard , name='create'),
)
