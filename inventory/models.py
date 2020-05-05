from django.db import models
from index.models import Player


class ConsumeItems(models.Model):
    name = models.CharField(max_length=250)
    max_stack = models.IntegerField()

    def __str__(self):
        return self.name


class CraftItems(models.Model):
    name = models.CharField(max_length=250)
    max_stack = models.IntegerField()

    def __str__(self):
        return self.name


class CraftRequirements(models.Model):
    craft_item = models.ForeignKey(CraftItems)
    consume_item = models.ForeignKey(ConsumeItems)
    craft_amount = models.IntegerField(blank=True, null=True)
    consume_amount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.consume_amount)+' '+self.consume_item.name+' --> '+str(self.craft_amount)+' '+self.craft_item.name


class Weapons(models.Model):
    name = models.CharField(max_length=250)
    steel = models.FloatField()
    wood = models.FloatField()
    leather = models.FloatField()
    focus = models.FloatField()
    focus_offset = models.FloatField()
    attack = models.FloatField()
    defence = models.FloatField()
    dmg = models.FloatField()
    dmg_offset = models.FloatField()
    stun = models.FloatField()
    deattack = models.FloatField()
    twohand = models.BooleanField()

    def __str__(self):
        return self.name


class Weapon(models.Model):
    static = models.ForeignKey(Weapons)
    level = models.IntegerField()
    quality = models.IntegerField()
    dur = models.IntegerField()

    def __str__(self):
        return self.static.name


class Semiproduct(models.Model):
    level = models.IntegerField()
    steel = models.FloatField()
    wood = models.FloatField()
    leather = models.FloatField()

    def __str__(self):
        return 'Semiproduct - ' + str(self.id)


class Armors(models.Model):
    name = models.CharField(max_length=250)
    steel = models.FloatField()
    wood = models.FloatField()
    leather = models.FloatField()
    min_movement = models.FloatField()
    absorb = models.FloatField()
    body_part = models.IntegerField()

    def __str__(self):
        return self.name


class Armor(models.Model):
    static = models.ForeignKey(Armors)
    level = models.IntegerField()
    quality = models.IntegerField()

    def __str__(self):
        return self.static.name


class Shields(models.Model):
    name = models.CharField(max_length=250)
    steel = models.FloatField()
    wood = models.FloatField()
    leather = models.FloatField()
    min_movement = models.FloatField()
    defence = models.FloatField()

    def __str__(self):
        return self.name


class Shield(models.Model):
    static = models.ForeignKey(Shields)
    level = models.IntegerField()
    quality = models.IntegerField()

    def __str__(self):
        return self.static.name


class Inventory(models.Model):
    player = models.ForeignKey(Player)
    pos = models.IntegerField()
    consume_items = models.ForeignKey(ConsumeItems, blank=True, null=True)
    craft_items = models.ForeignKey(CraftItems, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    weapon = models.ForeignKey(Weapon, blank=True, null=True, on_delete=models.CASCADE)
    armor = models.ForeignKey(Armor, blank=True, null=True, on_delete=models.CASCADE)
    shield = models.ForeignKey(Shield, blank=True, null=True, on_delete=models.CASCADE)
    semiproduct = models.ForeignKey(Semiproduct, blank=True, null=True, on_delete=models.CASCADE)
    equip = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (("player", "pos"),)

    def __str__(self):
        if self.craft_items:
            name = self.craft_items.name
        elif self.consume_items:
            name = self.consume_items.name
        elif self.weapon:
            name = self.weapon.static.name
        elif self.armor:
            name = self.armor.static.name
        elif self.shield:
            name = self.shield.static.name
        elif self.semiproduct:
            name = 'semiproduct'
        else:
            name = 'undefined'

        return 'Item_id: ' + str(self.id) + ' - ' + str(name) + ' (' + str(self.player.name) + ')'

