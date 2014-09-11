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

    url(r'^archive/recent/$', BlogPostArchiveIndexView.as_view(), name='archive_recent'),
    url(r'^archive/monthly/(?P<year>\d{4})/(?P<month>[a-z, A-Z]{3})/$', BlogPostMonthArchiveView.as_view(), name="monthly"),
    url(r'^archive/yearly/(?P<year>\d{4})/$', BlogPostYearArchiveView.as_view(), name="yearly"),

    # to view a blog post by pk in the url
    url(r'^newpost/$', BlogPostCreateView.as_view(), name='newblogpost'),
    url(r'^updatepost/(?P<pk>\d+)/$', BlogPostUpdateView.as_view(), name='updatepost'),
    url(r'^detailpost/(?P<pk>\d+)/$', BlogPostDetail.as_view(), name='detailpost'),
    # To view a blog-post by slug in the url
    #url(r'^detailpost/(?P<slug>[\w\-]+)/$', BlogPostDetail.as_view(), name='detailpost'),
)