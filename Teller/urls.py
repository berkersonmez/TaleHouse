from django.conf.urls import patterns, url

from Teller import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^user/add/$', views.user_add, name='user_add'),
                       url(r'^user/login/$', views.user_login, name='user_login'),
                       url(r'^user/logout/$', views.user_logout, name='user_logout'),
                       url(r'^tale/part/add$', views.tale_add_part, name='tale_add_part'),
                       url(r'^error/(?P<error_message>[\w ]+)$', views.error_info, name='error_info'),
)