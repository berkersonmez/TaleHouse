from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'TaleHouse.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^ckeditor/', include('ckeditor.urls')),
                       url(r'^captcha/', include('captcha.urls')),
                       url('', include('social.apps.django_app.urls', namespace='social')),
                       url(r'', include('Teller.urls')),
)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
                            (r'^upload/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT}))