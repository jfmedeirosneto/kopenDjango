from django.db import models

from kopenDjango.django_evolution.mutations import DeleteModel


MUTATIONS = [
    DeleteModel('Message')
]

