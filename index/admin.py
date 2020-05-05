from django.contrib import admin
from .models import Player, User
from django.conf import settings


# class PlayerAdmin(admin.ModelAdmin):
#     list_display = ('user', 'name', 'stamina', 'pos')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'active_player', 'is_staff', 'is_active')

admin.site.register(Player)
admin.site.register(User, UserAdmin)