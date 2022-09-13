from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Recipe


class CustomSearchFilter(SearchFilter):
    search_param = "name"


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='in')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
        ordering = ['id']

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset.filter(~Q(favorite__user=user))

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcart__user=user)
        return queryset.filter(~Q(shoppingcart__user=user))
