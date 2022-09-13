import datetime
from django.http import FileResponse
from fpdf import FPDF
import io
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph

from foodgram import settings
from .models import Ingredient, IngredientInRecipe, ShoppingCart


def download_shopping_cart(request):
    file_path = os.path.join(
        settings.MEDIA_ROOT,
        'recipes/shopping_cart/',
        str(request.user)
    )

    os.makedirs(file_path, exist_ok=True)
    file = os.path.join(
            file_path, str(datetime.datetime.now()) + '.txt')

    user = request.user
    purchases = ShoppingCart.objects.filter(user=user)

    with open(file, 'w') as f:
        cart = dict()
        for purchase in purchases:
            ingredients = IngredientInRecipe.objects.filter(
                recipe=purchase.recipe.id
            )
            for r in ingredients:
                i = Ingredient.objects.get(pk=r.ingredient.id)
                point_name = f'{i.name} ({i.measurement_unit})'
                if point_name in cart.keys():
                    cart[point_name] += r.amount
                else:
                    cart[point_name] = r.amount

        for name, amount in cart.items():
            f.write(f'* {name} - {amount}\n')

    return FileResponse(open(file, 'rb'), as_attachment=True)
