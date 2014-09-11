from django.views.generic import TemplateView
from django.views.generic.dates import ArchiveIndexView, MonthArchiveView, YearArchiveView
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
    url(r'^newpost/$', BlogPostCreateView.as_view(), name='newblogpost'),
    url(r'^archive/index/$', ArchiveIndexView.as_view(model=BlogPost, date_field="pub_date"), name='blogpost_archive'),
    
    #http://localhost:8000/archive/monthly/?year=2013&month=feb
    url(r'^archive/monthly/$', MonthArchiveView.as_view(model=BlogPost, date_field="pub_date", paginate_by=12), name='monthly'),
    url(r'^archive/monthly/(?P<year>\d{4})/(?P<month>\d+)/$', MonthArchiveView.as_view(model=BlogPost, date_field="pub_date", month_format='%m'), name="monthly2"),
    
    #http://localhost:8000/archive/yearly/?year=2013
    url(r'^archive/yearly/$', YearArchiveView.as_view(model=BlogPost, date_field="pub_date", make_object_list = True), name='yearly'),
    
    
    # To view a blog-post by slug in the url
    #url(r'^detailpost/(?P<slug>[\w\-]+)/$', BlogPostDetail.as_view(), name='detailpost'),
    
    # to view a blog post by pk in the url
    url(r'^detailpost/(?P<pk>\d+)/$', BlogPostDetail.as_view(), name='detailpost'),
    url(r'^updatepost/(?P<pk>\d+)/$', BlogPostUpdateView.as_view(), name='updatepost'),
)