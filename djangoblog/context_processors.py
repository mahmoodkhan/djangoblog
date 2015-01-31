import random

from django.conf import settings
from django.db.models import Count
from blog.models import *

def get_categories(self):
    categories = Category.objects.filter(blogposts__isnull=False).annotate(frequency=Count('blogposts')).order_by('name')
    return {'categories': categories}
        
def get_blogposts_archive_info(self):
    posts = BlogPost.objects.datetimes("pub_date", "month").filter(published=True).filter(private=False)
    prev_year = None
    years = {}
    months = []
    months_count = []
    for p in posts:
        if prev_year != None and prev_year != p.year:
            years[prev_year] = months
            months = []
        c = BlogPost.objects.filter(pub_date__year=p.year, pub_date__month=p.month).aggregate(Count('pk'))
        months_count.append(p.strftime("%b"))
        months_count.append(c['pk__count'])
        months.append(months_count)
        months_count = []
        prev_year = p.year
    if prev_year:
        years[prev_year] = months
    return {'archive_data': years}
        
def get_tag_cloud(self):
    tags = Tag.objects.filter(blogposts__isnull=False).annotate(frequency=Count('blogposts')).order_by('frequency')

    if not tags:
        return {}

    # This is the number of occurences for the most frequent tag.
    lo_freq = tags[0].frequency

    # This is the number of occurences for the least frequent tag.
    hi_freq = tags[len(tags) -1].frequency

    # The maximum font-size of the largest (most frequent) tag
    max_fontsize = 1.5
    
    # The minimum font-size of the smallest (least frequent) tag
    min_fontsize = 0.6
    
    # The display font-size used by the current tag
    display_fontsize = 0

    tags_dict = []
    if hi_freq - lo_freq != 0:
        multiplier = (max_fontsize-min_fontsize)/(hi_freq-lo_freq)
    else:
        multiplier = 1
    multiplier = float("{0:.2f}".format(multiplier))
    
    colors = ["#728FCE", "#357EC7", "#008080", "#254117", "#E2A76F", "#C88141", "#6F4E37", "#E78A61", "#C24641", "#7D0541", "#583759", "#837E7C", "#2C3539"]

    tags = Tag.objects.filter(blogposts__isnull=False).annotate(frequency=Count('blogposts'))
    
    for t in tags:
        display_fontsize =  min_fontsize + (hi_freq-(hi_freq-(t.frequency-lo_freq))) * multiplier
        display_fontsize = float("{0:.2f}".format(display_fontsize))
        font_color =  random.choice(colors) #''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        tags_dict.append({'id': t.id, 'name':t.name, 'frequency': t.frequency, 'fontsize': display_fontsize, 'color': font_color})
    return {'tags': tags_dict}

def google_analytics(request):
    """
    Use the variables returned in this function to
    render Google Analytics tracking code template.
    """
    ga_prop_id = getattr(settings, 'GOOGLE_ANALYTICS_PROPERTY_ID', False)
    ga_domain = getattr(settings, 'GOOGLE_ANALYTICS_DOMAIN', False)
    if not settings.DEBUG and ga_prop_id and ga_domain:
        return {
            'GOOGLE_ANALYTICS_PROPERTY_ID': ga_prop_id,
            'GOOGLE_ANALYTICS_DOMAIN': ga_domain,
        }
    return {}
