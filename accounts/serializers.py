from rest_framework import serializers
from .models import CustomUser, Invoice, Statement
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
        user = authenticate(request=self.context.get('request'), username=username,
                            password=password)
        if not user:
            raise serializers.ValidationError("Wrong Credentials.")

        attrs['user'] = user
        return attrs

class DepositSerializer(serializers.Serializer):
    depositMoney = serializers.IntegerField()
    def validate(self, attrs):
        depositMoney = attrs.get('depositMoney')
        if depositMoney < 0:
            raise serializers.ValidationError("The amount of money must be greater than zero!")
        return attrs

class InvoiceSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)
    class Meta:
        model = Invoice
        fields = ('PID', 'AID', 'orderId', 'totalAmount', 'airline', 'key')
    
    def create(self, validated_data):
        key = get_random_secret_key()
        validated_data['key'] = key
        return Invoice.objects.create(**validated_data)

class StatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statement
        fields = ('time', 'description', 'price', 'status')

class PaySerializer(serializers.Serializer):
    orderId = serializers.IntegerField()

    def validate(self, attrs):
        orderId = attrs.get('orderId')
        if not Invoice.objects.filter(orderId=orderId).exists():
            raise serializers.ValidationError('Order does not exist.')
        return attrs

class TransferSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    userName = serializers.CharField()
    transferMoney = serializers.FloatField()

    def validate(self, attrs):
        phoneNumber = attrs.get('phoneNumber')
        userName = attrs.get('userName')
        transferMoney = attrs.get('transferMoney')
        if not CustomUser.objects.filter(username=phoneNumber).exists():
            raise serializers.ValidationError('Phone number does not exist.')
        payee = CustomUser.objects.get(username=phoneNumber)
        if payee.name != userName:
            raise serializers.ValidationError('Phone number does not exist.')
        return attrs