from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name',
                    'last_name', 'email', 'is_staff')
    list_filter = ('email', 'first_name')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
