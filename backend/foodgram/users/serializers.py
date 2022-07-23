from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from subscriptions.models import Subscription
from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, instance):
        subscriber = self.context.get('request').user
        subscription_instance = Subscription.objects.filter(
            author=instance, subscriber=subscriber)
        if subscription_instance.exists():
            return True
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        label='Адрес электронной почты',
        max_length=254,
        validators=[UniqueValidator])
    username = serializers.CharField(
        label='Имя пользователя',
        max_length=150,
        validators=[UniqueValidator])
    first_name = serializers.CharField(
        label='Имя',
        max_length=150,
        required=True)
    last_name = serializers.CharField(
        label='Фамилия',
        max_length=150,
        required=True)
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
