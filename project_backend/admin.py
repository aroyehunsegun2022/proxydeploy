from django.contrib import admin

from project_backend import models

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'phoneNumber',
        'city',
        'user_type',
        'is_verified',
        'is_active',
        'created_at'
    )
    
admin.site.register(models.User, UserAdmin)