from django.views.generic import TemplateView
from django.conf.urls import patterns, include, url
from django.contrib import admin
from blog.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="blog/index.html"), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),
    url(r'^newpost/$', BlogPostCreate.as_view(), name='newblogpost'),
    #url(r'^$', 'blog.views.index', name='home'),
    #url(r'^(?P<slug>[\w\-]+)/$', 'blog.views.post'),
)