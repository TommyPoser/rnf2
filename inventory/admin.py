from django.contrib import admin
from .models import ConsumeItems, Weapons, Weapon, Armors, Armor, Shields, Shield, Inventory


class ConsumeItemsAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_stack')

admin.site.register(ConsumeItems, ConsumeItemsAdmin)
admin.site.register(Weapons)
admin.site.register(Weapon)
admin.site.register(Armors)
admin.site.register(Armor)
admin.site.register(Shields)
admin.site.register(Shield)

admin.site.register(Inventory)
