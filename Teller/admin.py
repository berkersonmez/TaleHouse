from django.contrib import admin
from Teller.models import *
from django.contrib.auth.admin import UserAdmin


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    #prepopulated_fields = {'slug': ('parent_username',)}


class UserProfileAdmin(UserAdmin):
    inlines = (ProfileInline, )


class TaleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class TalePartAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.register(Tale, TaleAdmin)
admin.site.register(TalePart, TalePartAdmin)
admin.site.register(Profile)
admin.site.register(TaleLink)
admin.site.register(Language)