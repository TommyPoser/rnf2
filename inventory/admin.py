from django.contrib import admin
from .models import ConsumeItems, CraftItems, CraftRequirements,\
                    Weapons, Weapon,\
                    Armors, Armor,\
                    Shields, Shield,\
                    Semiproduct, \
                    Inventory


class ConsumeItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'max_stack')


admin.site.register(ConsumeItems, ConsumeItemsAdmin)
admin.site.register(CraftItems, ConsumeItemsAdmin)
admin.site.register(Weapons)
admin.site.register(Weapon)
admin.site.register(Armors)
admin.site.register(Armor)
admin.site.register(Shields)
admin.site.register(Shield)
admin.site.register(Semiproduct)
admin.site.register(CraftRequirements)

admin.site.register(Inventory)
