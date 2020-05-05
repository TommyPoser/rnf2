from django.db import models


class Pixel(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    z = models.FloatField()
    biome = models.IntegerField()

    def __str__(self):
        return 'x: ' + str(self.x) + ' y: ' + str(self.y) + ' z: ' + str(self.z) + ' biome:' + str(self.biome)


class Town(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Hexa(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    biome = models.IntegerField()
    grass = models.IntegerField()
    wood = models.IntegerField()
    hills = models.IntegerField()
    mountains = models.IntegerField()
    water = models.IntegerField()
    town = models.ForeignKey(Town, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.town:
            town_name = self.town.name
        else:
            town_name = ''

        return 'x: ' + str(self.x) + ' y: ' + str(self.y) + ' biome:' + str(self.biome) + ' town: ' + town_name



