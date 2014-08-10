from django.views.generic import TemplateView
from django.conf.urls import patterns, include, url
from django.contrib import admin
from blog.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="blog/index.html")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^about/$', TemplateView.as_view(template_name='blog/about.html')),
    #url(r'^$', 'blog.views.index', name='home'),
    #url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    #url(r'^(?P<slug>[\w\-]+)/$', 'blog.views.post'),
)