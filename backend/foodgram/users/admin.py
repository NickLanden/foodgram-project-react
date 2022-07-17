from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')
    list_filter = ('email', 'first_name')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
