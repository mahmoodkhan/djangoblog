from django.contrib import admin
from blog.models import *

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    display_fields = ["name", "description", ]


class TagAdmin(admin.ModelAdmin):
    display_fields = ["name", "created",]

class PostAdmin(admin.ModelAdmin):
    # fields display on change list
    list_display = ['title', 'category',]
    
    # fields to filter the change list with
    list_filter = ['published', 'created']
    
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

class CommentAdmin(admin.ModelAdmin):
    display_fields = ["author", "post", "pub_date",]

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
