from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Activity, ResourceVideo


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'level', 'age_min', 'age_max', 'is_active', 'order']
    list_filter   = ['category', 'level', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']


@admin.register(ResourceVideo)
class ResourceVideoAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'age_min', 'age_max', 'is_active', 'order']
    list_filter   = ['category', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']