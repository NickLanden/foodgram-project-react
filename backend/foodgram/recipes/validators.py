from django.core.exceptions import ValidationError


def validate_integer_greater_zero(value):
    if value < 1:
        raise ValidationError(
            'Время приготовления не должно быть меньше единицы!')
