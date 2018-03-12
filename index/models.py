from django.db import models
from django.contrib.auth.models import Permission, AbstractUser


class User(AbstractUser):
    active_player = models.IntegerField(null=True, default=0)


class Player (models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=250)
    stamina = models.IntegerField(null=True, default=30)

    def __str__(self):
        return self.name
