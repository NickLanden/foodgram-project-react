from django.shortcuts import get_object_or_404
from djoser import utils
from djoser.serializers import (SetPasswordSerializer,
                                TokenCreateSerializer,
                                TokenSerializer)
from djoser.views import TokenCreateView
from rest_framework import mixins, status, viewsets
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.permissions import IsAuthor
from recipes.views import get_object_or_400
from .models import Subscription, User
from .serializers import (
    SubscriptionSerializer,
    UserForSubscriptionSerializer,
    UserSerializer,
    UserCreateSerializer
)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'subscriptions':
            return SubscriptionSerializer
        else:
            return UserSerializer

    def get_permissions(self):
        if self.action in ('list', 'create'):
            self.permission_classes = [AllowAny]
        elif self.action in ('retrieve', 'me'):
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'subscribe':
            self.permission_classes = [IsAuthor]
        elif self.action == 'subscriptions':
            self.permission_classes = [IsAuthor]
        return super().get_permissions()

    @action(methods=['get'], detail=False,
            url_path='me', url_name='me')
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.data.get('new_password'))
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписываться/отписывать от самого себя!')

        if request.method == 'POST':
            if Subscription.objects.filter(
                    author=author, subscriber=user):
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя!')

            Subscription.objects.create(
                author=author,
                subscriber=user
            )
            serializer = UserForSubscriptionSerializer(author)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        else:
            subscription = get_object_or_400(
                Subscription,
                'Вы не подписаны на этого пользователя!',
                author=author,
                subscriber=user
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = request.user
        subscriptions = user.subscriber.all()

        page = self.paginate_queryset(subscriptions)

        authors = []

        for p in page:
            author = p.author
            authors.append(author)
        serializer = UserForSubscriptionSerializer(authors, many=True)

        return self.get_paginated_response(serializer.data)


class TokenCreateView(TokenCreateView):
    serializer_class = TokenCreateSerializer
    permission_classes = (AllowAny,)

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = TokenSerializer
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )
