from recipes.models import AmountIngredients, Recipe
from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404


def recipe_ingredients_set(recipe, ingredients):
    objs = []

    for ingredient, amount in ingredients.values():
        objs.append(
            AmountIngredients(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        )

    AmountIngredients.objects.bulk_create(objs)


def obj_in_table(user, object, model):
    """
    Определяет, есть ли запрашиваемый рецепт (object) в:
    - избранных рецептах, если в качестве model передали модель Favourite,
    - списке рецептов к покупке, если в качестве model передали ShoppingCart.
    """

    if not user.id:
        # запрос от анонимного пользователя
        return False
    recipe = model.objects.filter(
        user=user,
        recipe=object,
    )
    return recipe.exists()


def delete_dependence(model, user, pk):
    item = model.objects.filter(
        user=user,
        recipe=get_object_or_404(Recipe, id=pk)
    )
    if item.exists():
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'Запрашиваемый объект не найден!'},
        status=status.HTTP_400_BAD_REQUEST
    )


def create_dependence(serializer, user, pk):
    serializers = serializer(data={'user': user.id, 'recipe': pk})
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
