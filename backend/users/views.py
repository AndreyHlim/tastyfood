from api.permissions import AuthorStaffOrReadOnly
from api.serializers import (
    FollowAddSerializer,
    FollowSerializer,
    ProfileSerializer
)
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from django.shortcuts import get_object_or_404


class ProfileViewSet(UserViewSet):
    http_method_names = ['get', 'post', 'delete']
    pagination_class = LimitOffsetPagination
    serializer_class = ProfileSerializer

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        if self.action in ['subscribe', 'delete_subscribe']:
            return (AuthorStaffOrReadOnly(),)
        return (AllowAny(),)

    @action(
        detail=False,
        methods=['get'],
    )
    def subscriptions(self, request):
        user = request.user
        followings = Follow.objects.filter(user=user)
        queryset = User.objects.filter(
            id__in=followings.values_list('following')
        )
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
    )
    def subscribe(self, request, id):
        # postman хочет 404, а сериализатор выдаст 400
        get_object_or_404(User, id=id)
        serializer = FollowAddSerializer(
            data={'user': request.user.id, 'following': id},
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        following = Follow.objects.filter(
            user=request.user,
            following=get_object_or_404(User, id=id)
        )
        if not following.exists():
            return Response(
                {'errors': 'Запрашиваемой подписки не сущестовало!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
