import datetime
from haystack import indexes
from .models import BlogPost

class BlogPostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title', faceted=True)
    pub_date = indexes.DateTimeField(model_attr='pub_date', faceted=True)
    
    def get_model(self):
        return BlogPost
    
    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(published=True, private=False)