from django.conf.urls import patterns, include, url
from django.contrib import admin
from blog.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^ZmaTheWebsiteAdminPanelDaltaDai1484/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root': settings.STATIC_ROOT}),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^category/(?P<category>\d+)/$', HomeView.as_view(), name='home_category'),
    url(r'^tag/(?P<tags>\d+)/$', HomeView.as_view(), name='home_tag'),

    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    url(r'^about/$', AboutView.as_view(), name='about'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),

    url(r'^archive/recent/$', BlogPostArchiveIndexView.as_view(), name='archive_recent'),
    url(r'^archive/monthly/(?P<year>\d{4})/(?P<month>[a-z, A-Z]{3})/$', BlogPostMonthArchiveView.as_view(), name="monthly"),
    url(r'^archive/yearly/(?P<year>\d{4})/$', BlogPostYearArchiveView.as_view(), name="yearly"),

    url(r'^newpost/$', BlogPostCreateView.as_view(), name='newblogpost'),

    # to view a blog post by pk in the url
    url(r'^updatepost/(?P<pk>\d+)/$', BlogPostUpdateView.as_view(), name='updatepost'),
    url(r'^detailpost/(?P<pk>\d+)/$', BlogPostDetail.as_view(), name='detailpost'),

    # To view a blog-post by slug in the url
    #url(r'^detailpost/(?P<slug>[\w\-]+)/$', BlogPostDetail.as_view(), name='detailpost'),


    #Instead of using haystack.urls I use my own search view so that I can override the
    #"extra_context method and provide additional data
    #url(r'^search/', include('haystack.urls')),
    url(r'^search/', Search(), name='haystack_search'),
)
