from django.db import models
from index.models import Player


class Animal(models.Model):
    name = models.CharField(max_length=250)
    biome = models.IntegerField()
    presence = models.IntegerField()
    aggression = models.IntegerField()
    shots = models.IntegerField()
    size = models.IntegerField()
    meat = models.IntegerField()
    leather = models.IntegerField()
    feather = models.IntegerField()
    scales = models.IntegerField()
    venom = models.IntegerField()
    light_blood = models.IntegerField()

    def __str__(self):
        return self.name


class Hunt(models.Model):
    player = models.ForeignKey(Player)
    animal = models.ForeignKey(Animal)
    behaviour = models.IntegerField(default=0)  # idle/attacking/running/dead
    hit_chance = models.IntegerField()
    hits = models.IntegerField(default=0)
    slot = models.IntegerField()

    def __str__(self):
        return str(self.pk) + ' - ' + self.player.name + ' | ' + self.animal.name

