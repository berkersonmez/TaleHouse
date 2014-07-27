from django.conf.urls import patterns, url

from Teller import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^user/add/$', views.user_add, name='user_add'),
                       url(r'^user/login/$', views.user_login, name='user_login'),
                       url(r'^user/logout/$', views.user_logout, name='user_logout'),
                       url(r'^tale/part/add$', views.tale_add_part, name='tale_add_part'),
                       url(r'^tale/part/add/(?P<tale_slug>[\w-]+)$', views.tale_add_part, name='tale_add_part_idgiven'),
                       url(r'^tale/link/add/(?P<tale_slug>[\w-]+)$', views.tale_add_link, name='tale_add_link'),
                       url(r'^tale/part/edit/(?P<tale_part_id>[\d-]+)$', views.tale_edit_part, name='tale_edit_part'),
                       url(r'^tale/part/delete/(?P<tale_part_id>[\d-]+)$', views.tale_delete_part,
                           name='tale_delete_part'),
                       url(r'^tale/link/edit/(?P<tale_link_id>[\d-]+)$', views.tale_edit_link, name='tale_edit_link'),
                       url(r'^tale/link/delete/(?P<tale_link_id>[\d-]+)$', views.tale_delete_link,
                           name='tale_delete_link'),
                       url(r'^tale/delete/(?P<tale_id>[\d-]+)$', views.tale_delete, name='tale_delete'),
                       url(r'^tale/read/(?P<tale_slug>[\w-]+)/(?P<page_no>[\d-]+)$', views.tale_read, name='tale_read'),
                       url(r'^tale/read/(?P<tale_slug>[\w-]+)$', views.tale_read, name='tale_read_continue'),
                       url(r'^tale/add$', views.tale_add, name='tale_add'),
                       url(r'^tale/list$', views.tale_list, name='tale_list'),
                       url(r'^error/(?P<error_message>[\w ]+)$', views.error_info, name='error_info'),
                       url(r'^tale/details/(?P<tale_slug>[\w-]+)$', views.tale_details, name='tale_details'),
                       url(r'^test$', views.test, name='test'),
                       url(
                           r'^tale/vote/(?P<tale_slug>[\w-]+)/(?P<tale_link_id>[\d-]+)/(?P<tale_part_id>[\d-]+)/(?P<page_no>[\d-]+)$',
                           views.tale_vote, name='tale_vote'),
                       url(r'^tale/reset/(?P<tale_slug>[\w-]+)$', views.tale_reset, name='tale_reset'),
                       url(r'^tale/publish/(?P<tale_id>[\d-]+)$', views.tale_publish, name='tale_publish'),
                       url(r'^user/list$', views.user_list, name='user_list'),
                       url(r'^user/profile/(?P<user_username>[\w-]+)$', views.user_profile, name='user_profile'),
)