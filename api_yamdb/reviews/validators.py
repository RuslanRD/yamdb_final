from django.utils import timezone

from rest_framework import validators


def title_year_validator(value):
    if value > timezone.now().year:
        raise validators.ValidationError(
            (f'{value}s is not a correcrt year!')
        )
