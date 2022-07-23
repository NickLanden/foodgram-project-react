from rest_framework import serializers

from .models import Purchase


class PurchaseRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase
        fields = ('')
