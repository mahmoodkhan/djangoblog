import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=254, null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    
    def __unicode__(self):
        return unicode("%s (%s)" % (self.name, self.description))

    def get_absolute_url(self):
        """
        Used when we need to link to a specific category
        """
        return reverse('blog.views.post', args=[str(self.id)])


class Tag(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(User, related_name='tags')
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    
    def __unicode__(self):
        return unicode("%s (%s)" % (self.name, self.owner))

    def get_absolute_url(self):
        """
        Used when we need to link to a specific Tag.
        """
        return reverse('blog.views.post', args=[str(self.id)])


class Post(models.Model):
    """
        A post is the building block of a Blog; post cannot be cross-posted to multiple blogs
        A post can only be in one blog
        A post could have zero or many comments
    """
    title = models.CharField(max_length=64)
    slug = models.SlugField(unique=True, max_length=254)
    content = models.TextField()
    annotation = models.TextField(null=True, blank=True)
    published = models.BooleanField(default=False)
    pub_date = models.DateTimeField(null=True, blank=True)
    private = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
    owner = models.ForeignKey(User, related_name = 'posts')
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created',]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __unicode__(self):
        return unicode("%s (%s)" % (self.title, self.owner))

    def get_absolute_url(self):
        """
        Used when we need to link to a specific blog post.
        """
        return reverse('blog.views.post', args=[str(self.slug)])

class Attachment(models.Model):
    attachment = models.FileField(upload_to='attachments')
    post = models.ForeignKey(Post, related_name = 'attachments')
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def get_absolute_url(self):
        """
        Used when we need to link to a specific blog post.
        """
        return reverse('blog.views.post', args=[str(self.id)])
    

class Comment(models.Model):
    """
        A comment has an owner
        A comment belongs to a single post
    """
    author = models.TextField(max_length=64)
    body = models.TextField()
    post = models.ForeignKey(Post, related_name='comments')
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['author',]
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __unicode__(self):
        return unicode("%s: %s" % (self.post, self.body[:64]))

    def get_absolute_url(self):
        """
        Used when we need to link to a specific blog post.
        """
        return reverse('blog.views.comment', args=[str(self.id)])