from django.views.generic import TemplateView
from django.conf.urls import patterns, include, url
from django.contrib import admin
from blog.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),
    url(r'^newpost/$', BlogPostCreateUpdateView.as_view(), name='newblogpost'),
    
    # To view a blog-post by slug in the url
    #url(r'^detailpost/(?P<slug>[\w\-]+)/$', BlogPostDetail.as_view(), name='detailpost'),
    
    # to view a blog post by pk in the url
    url(r'^detailpost/(?P<pk>\d+)/$', BlogPostDetail.as_view(), name='detailpost'),
    url(r'^updatepost/(?P<pk>\d+)/$', BlogPostCreateUpdateView.as_view(), name='updatepost'),
)