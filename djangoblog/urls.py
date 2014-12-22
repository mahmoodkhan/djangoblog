from django.conf.urls import patterns, include, url
from django.contrib import admin
from blog.views import *
from blog.google import *

admin.autodiscover()
# regular reference:
# . any char
# ^ start of string 
# $ end of string
# * 0 or more of preceding 
# + 1 or more of preceding
# ? 0 or 1 of preceding 
# (?!..) matches when it doesnt match ..
# *? 0 or more, minimal match 
# +? 1 or more, minimal match
# {m} exactly m of preceding 
# {m,n} between m to n of preceding
# [..] eg. [abc],[a-z],[0-9a-z] 
# [^..] matches if doesn't match [..]
# (..) groups what's inside 
# (?=..) matches .. but doesn't consume it
# \d [0-9] (decimal digit)
# \D [^0-9] (non-digit)
# \w [a-zA-Z0-9_] (alphanumeric) 
# \W [^a-zA-Z0-9_] (non-alphanumeric)
# \s [ \t\n\r\f\v] (whitespace) 
# \S [^ \t\n\r\f\v] (non-whitespace)

urlpatterns = patterns('',
    url(r'^ZmaTheWebsiteAdminPanelDaltaDai1484/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root': settings.STATIC_ROOT}),
    
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^category/(?P<category>\d+)/$', HomeView.as_view(), name='home_category'),
    url(r'^tag/(?P<tags>\d+)/$', HomeView.as_view(), name='home_tag'),
    url(r'^hidden/(?P<published>[a-z, A-Z]{4,5})/(?P<private>[a-z, A-Z]{4,5})/$', HiddenBlogPost.as_view(), name='hidden_view'),

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

    url(r'^create_comment/$', CreateCommentView.as_view(), name='create_comment'),
    # To view a blog-post by slug in the url
    #url(r'^detailpost/(?P<slug>[\w\-]+)/$', BlogPostDetail.as_view(), name='detailpost'),

    url(r'^google/$', GoogleSingInView.as_view(), name='google_sign_in'),

    #Instead of using haystack.urls I use my own search view so that I can override the
    #"extra_context method and provide additional data
    #url(r'^search/', include('haystack.urls')),
    url(r'^search/', Search(), name='haystack_search'),
)
