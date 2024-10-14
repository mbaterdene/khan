from django.contrib import admin

# Register your models here.
from .models import defualtInfo
from import_export.admin import ImportExportModelAdmin



@admin.register(defualtInfo)
class BlogTyped(ImportExportModelAdmin):
    pass