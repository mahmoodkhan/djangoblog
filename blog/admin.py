from django.contrib import admin
from blog.models import *

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    display_fields = ["name", "description", ]


class TagAdmin(admin.ModelAdmin):
    display_fields = ["name", "created",]

class BlogPostAdmin(admin.ModelAdmin):
    # fields display on change list
    list_display = ['title', 'category',]
    
    # fields to filter the change list with
    list_filter = ['title', 'published', 'created']
    
    # fields to search in change list
    search_fields = ['title', 'content']
    
    # enable the date drill down on change list
    date_hierarchy = 'created'
    
    # enable the save buttons on top on change form
    save_on_top = True
    
    # prepopulate the slug from the title - big timesaver!
    prepopulated_fields = {"slug": ("title",)}

    display_fields = ["title", "pub_date", "private", "created", "updated",]

class AttachmentAdmin(admin.ModelAdmin):
    pass

class CommenterAdmin(admin.ModelAdmin):
    display_fields = ["email", "given_name", "family_name", "gender", "", ]

class CommentAdmin(admin.ModelAdmin):
    display_fields = ["author", "blogpost", "pub_date",]

admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Commenter, CommenterAdmin)
