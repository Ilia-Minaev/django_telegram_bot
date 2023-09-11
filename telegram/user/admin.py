from django.contrib import admin

from user.models import UserModels

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname', 'phone')
    list_display_links = ('id',)

admin.site.register(UserModels, UserAdmin)