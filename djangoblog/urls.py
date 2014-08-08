from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'blog.views.index', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<slug>[\w\-]+)/$', 'blog.views.post'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
)