from django_filters import rest_framework as filter
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filter.FilterSet):
    author = filter.CharFilter()
    tags = filter.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        label='Tags',
        to_field_name='slug',
    )
    is_favorited = filter.BooleanFilter(method='get_favorite')
    is_in_shopping_cart = filter.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user_id=self.request.user.id)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping__user_id=self.request.user.id)
        return queryset
