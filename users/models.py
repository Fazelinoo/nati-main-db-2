from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.TextChoices):
    HEAD_OF_TEAM = 'head_of_team', 'Head of Team'
    ART_DIRECTOR = 'art_director', 'Art Director'
    MUSIC_PRODUCER = 'music_producer', 'Music Producer'
    CG_DESIGNER = 'cg_designer', 'CG Designer'
    HEAD_OF_IT = 'head_of_it', 'Head of IT'
    IT_GUY = 'it_guy', 'IT Guy'


class CustomUser(AbstractUser):

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.HEAD_OF_TEAM)
    last_seen = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

