from django.contrib import admin
from Teller.models import *
from django.contrib.auth.admin import UserAdmin


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    #prepopulated_fields = {'slug': ('parent_username',)}


class UserProfileAdmin(UserAdmin):
    inlines = (ProfileInline, )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

    def user(self, obj):
        return obj.user.username

    user.short_description = 'User'


class TaleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.register(Tale, TaleAdmin)
admin.site.register(TalePart)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(TaleLink)
admin.site.register(TaleVariable)
admin.site.register(UserTaleVariable)
admin.site.register(Language)
admin.site.register(TaleLinkPrecondition)
admin.site.register(TaleLinkConsequence)