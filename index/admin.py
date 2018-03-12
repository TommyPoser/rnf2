from django.contrib import admin
from .models import Player, User
from django.conf import settings


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'stamina')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'active_player', 'is_staff', 'is_active')

admin.site.register(Player, PlayerAdmin)
admin.site.register(User, UserAdmin)