import datetime
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=254, null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """
        Used when we need to link to a specific category
        """
        return reverse('blog.views.blogpost', args=[str(self.id)])


class Tag(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(User, related_name='tags')
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """
        Used when we need to link to a specific Tag.
        """
        return reverse('blog.views.blogpost', args=[str(self.id)])

class BlogPost(models.Model):
    """
        A blogpost is the building block of a Blog; blogpost cannot be cross-blogposted to multiple blogs
        A blogpost can only be in one blog
        A blogpost could have zero or many comments
    """
    title = models.CharField(max_length=64, db_index=True)
    slug = models.SlugField(unique=True, max_length=64)
    content = models.TextField()
    annotation = models.TextField(null=True, blank=True)
    published = models.BooleanField(default=False)
    pub_date = models.DateTimeField(null=True, blank=True)
    private = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name='blogposts')
    tags = models.ManyToManyField(Tag, related_name='blogposts')
    owner = models.ForeignKey(User, related_name = 'blogposts')
    lastaccessed = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created',]
        verbose_name = 'BlogPost'
        verbose_name_plural = 'BlogPosts'

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return ("%s (%s)" % (self.title, self.owner))
    
    def get_absolute_url(self):
        """
        Used when we need to link to a specific blog post.
        """
        return reverse('detailpost', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        if self.pk is None:        
            """ To automatically create the slug """
            #self.slug = '%i-%s' % (self.id, slugify(self.title))
            self.slug = slugify(self.title)
        super(BlogPost, self).save(*args, **kwargs)

class Attachment(models.Model):
    attachment = models.FileField(upload_to='attachments')
    blogpost = models.ForeignKey(BlogPost, related_name = 'attachments')
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def get_absolute_url(self):
        """
        Used when we need to link to a specific blog post.
        """
        return reverse('blog.views.blogpost', args=[str(self.id)])
    

class Comment(models.Model):
    """
        A comment has an owner
        A comment belongs to a single blogpost
    """
    author = models.TextField(max_length=64)
    body = models.TextField()
    blogpost = models.ForeignKey(BlogPost, related_name='comments')
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['author',]
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return ("%s (%s)" % (self.name, self.owner))
    
    def get_absolute_url(self):
        """
        Used when we need to link to a specific blog post.
        """
        return reverse('blog.views.comment', args=[str(self.id)])