from django.db import models
from index.models import Player


class ConsumeItems(models.Model):
    name = models.CharField(max_length=250)
    max_stack = models.IntegerField()

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class Weapon(models.Model):
    static = models.ForeignKey(Weapons)
    level = models.IntegerField()
    quality = models.IntegerField()
    dur = models.IntegerField()

    def __str__(self):
        return self.static.name


class Armors(models.Model):
    name = models.CharField(max_length=250)
    steel = models.FloatField()
    wood = models.FloatField()
    leather = models.FloatField()
    min_movement = models.FloatField()
    absorb = models.FloatField()

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
    amount = models.IntegerField(blank=True, null=True)
    weapon = models.ForeignKey(Weapon, blank=True, null=True)
    armor = models.ForeignKey(Armor, blank=True, null=True)
    shield = models.ForeignKey(Shield, blank=True, null=True)

    class Meta:
        unique_together = (("player", "pos"),)

    def __str__(self):
        if self.consume_items:
            name = self.consume_items.name
        elif self.weapon:
            name = self.weapon.static.name
        else:
            name = 'undefined'

        return 'Item_id: ' + str(self.id) + ' - ' + str(name) + ' (' + str(self.player.name) + ')'

