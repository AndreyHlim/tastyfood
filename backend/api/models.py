from django.db import models
from django.contrib.auth.models import AbstractUser
from api.validators import validate_username
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
# from django.db.models import Q, F


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Profile(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150)
    username = models.CharField(
        max_length=150, unique=True,
        validators=(validate_username,)
    )
    last_name = models.CharField(max_length=150)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'username', 'last_name',]

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.email} ({self.username})'


User = get_user_model()


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AmountIngredients',
        verbose_name='Ингредиенты для приготовления',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег(-и)',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/images/',
        # null=True,
        # blank=True,
        # default=None,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    text = models.CharField(
        verbose_name='Описание рецепта',
        max_length=1000,
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(1,),
        )
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        # image = Image.open(self.image.path)
        # image.thumbnail(Tuples.RECIPE_IMAGE_SIZE)
        # image.save(self.image.path)


class AmountIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    amount = models.IntegerField(
        validators=(
            MinValueValidator(1,),
        )
    )

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['recipe', 'ingredient'],
    #             name='unique_recipe_ingredient'
    #         )
    #     ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='На кого подписан'
    )

    class Meta:
        verbose_name = 'подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_subscriptions'
            ),
            # models.CheckConstraint(
            #     check=~Q(user=F("following")),
            #     name='Подписака на самого себя'
            # ),
        ]

    def __str__(self):
        return ('{} подписан на рецепты {}'.format(self.user, self.following))


class Favourite(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourites'
            )
        ]

    def __str__(self):
        return (f'Пользователь {self.user} добавил '
                f'рецепт "{self.recipe}" себе в избранное')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_add_recipes'
            )
        ]

    def __str__(self):
        return (f'Пользователь {self.user} планирует купить '
                f'ингредиенты рецепта: {self.recipe}')