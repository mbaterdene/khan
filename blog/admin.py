from django.contrib import admin
from .models import Blog, BlogType, Tag
# from import_export.admin import ImportExportModelAdmin


# @admin.register(BlogType)
# class BlogTyped(ImportExportModelAdmin):
#     pass


# @admin.register(Tag)
# class Viewtag(ImportExportModelAdmin):
#     pass

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_time', 'last_updated_time')  # Fields displayed in the admin list view
    search_fields = ('title', 'content')  # Add a search bar for title and content
    
    filter_horizontal = ('tags',)  # Enables a horizontal filter widget for the ManyToManyField
   
    verbose_name_plural = 'Нийтлэл'