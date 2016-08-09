from django.db import models

from kopenDjango.django_evolution.mutations import ChangeField


MUTATIONS = [
    ChangeField('Session', 'expire_date', initial=None, db_index=True)
]
