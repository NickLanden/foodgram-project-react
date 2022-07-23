from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .permissions import CurrentUserOrAdmin
from .serializers import UserSerializer, UserCreateSerializer


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    # serializer_class = UserSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        else:
            return UserSerializer

    def get_permissions(self):
        if self.action in ('list', 'create'):
            self.permission_classes = [AllowAny]
        elif self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(methods=['get'], detail=False,
            url_path='me', url_name='me')
    def me(self, request):
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data.get('new_password'))
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
