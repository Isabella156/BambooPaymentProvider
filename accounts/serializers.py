from rest_framework import serializers
from .models import CustomUser, Invoice
from django.contrib.auth import authenticate
import hashlib
from phonenumbers import parse as phonenumbers_parse
import phonenumbers
from django.core.management.utils import get_random_secret_key

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'nickname', 'name', 'user_id_number', 'user_phone', 'user_email', 'password', 'balance')

class SignupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('nickname', 'name', 'user_id_number', 'user_phone', 'user_email', 'password')
        # fields = '__all__'
        # extra_kwargs = {
        #     'password': {'required': True}
        # }
    def validate(self, attrs):
        user_phone = attrs.get('user_phone')
        if CustomUser.objects.filter(user_phone=user_phone).exists():
            raise serializers.ValidationError('User with this phone number already exists.')
        return attrs

    def create(self, validated_data):
        print(validated_data)
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        parsed_phone = phonenumbers_parse(username, None)
        print(username)
        if not username:
        	raise serializers.ValidationError("Please give username.")
        if not password:
            raise serializers.ValidationError("Please give password.")
        if not phonenumbers.is_valid_number(parsed_phone):
            raise serializers.ValidationError('Invalid phone number')

        if not CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError('Phone number does not exist.')

        # user = authenticate(request=self.context.get('request'), username=username,
                            # password=password)
        user = authenticate(request=self.context.get('request'), username='+8613281129456',
                            password='123456')
        if not user:
            raise serializers.ValidationError("Wrong Credentials.")

        attrs['user'] = user
        return attrs

class DepositSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    def validate(self, attrs):
        amount = attrs.get('amount')
        if amount < 0:
            raise serializers.ValidationError("The amount of money must be greater than zero!")
        return attrs

class InvoiceSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)
    class Meta:
        model = Invoice
        fields = ('id', 'aid', 'order_id', 'totalAmount', 'airline', 'key')
    
    def create(self, validated_data):
        key = get_random_secret_key()
        validated_data['key'] = key
        return Invoice.objects.create(**validated_data)

class PaySerializer(serializers.Serializer):
    orderId = serializers.IntegerField()
    print(orderId)

    def validate(self, attrs):
        orderId = attrs.get('orderId')
        print(orderId)
        if not Invoice.objects.filter(order_id=orderId).exists():
            raise serializers.ValidationError('Order does not exist.')
        return attrs