from djoser.serializers import (SetPasswordSerializer,
                                TokenCreateSerializer,
                                TokenSerializer)
from djoser import utils
from djoser.views import TokenCreateView
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import (
    # SubscriptionSerializer,
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
        # elif self.action == 'subscription':
        #     return SubscriptionSerializer
        else:
            return UserSerializer

    def get_permissions(self):
        print(self.action)
        if self.action in ('list', 'create'):
            self.permission_classes = [AllowAny]
        elif self.action in ('retrieve', 'me', 'subscriptions'):
            self.permission_classes = [IsAuthenticated]
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
        self.request.user.set_password(serializer.data.get('new_password'))
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(methods=['get'], detail=False)
    # def subscriptions(self, request):
    #     user = request.user
    #     subs = Subscription.objects.filter(subscriber=user)
    #     authors = [x.author for x in subs]
    #     print(authors)
    #     serializer = self.get_serializer(authors, many=True)
    #     print(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


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
