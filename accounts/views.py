from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from .models import CustomUser, Invoice, Statement
from rest_framework.response import Response
from rest_framework import status, authentication, generics, permissions
from rest_framework.generics import GenericAPIView
from .serializers import SignupUserSerializer, LoginSerializer, UserSerializer, DepositSerializer, InvoiceSerializer, PaySerializer
from rest_framework.permissions import AllowAny
from knox import views as knox_views
from django.contrib.auth import login
from knox.auth import TokenAuthentication
import datetime
from django.db import transaction

class CreateUserAPI(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignupUserSerializer
    permission_classes = (AllowAny,)

class SigninAPIView(knox_views.LoginView):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
            response = super().post(request, format=None)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response.data, status=status.HTTP_200_OK)

class DepositView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = DepositSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        user_id = request.user.id
        if serializer.is_valid(raise_exception=True):
            amount = serializer.validated_data['amount']
            user = CustomUser.objects.get(pk=user_id)
            # deposit money
            user.balance += amount
            balance = user.balance
            user.save()
            return Response({'user_balance': balance})
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class InvoiceView(CreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    
class PayView(GenericAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = PaySerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        user_id = request.user.id
        if serializer.is_valid(raise_exception=True):
            orderId = serializer.validated_data['orderId']
            invoice = Invoice.objects.get(order_id=orderId)
            amount = invoice.totalAmount
            airline = getattr(invoice, 'airline')
            key = getattr(invoice, 'key')
            user = CustomUser.objects.get(pk=user_id)

            # airline dictionary
            airline_dictionary = {
                'airline1': ['+8618301234567'],
                'airline2': ['+8613507654321'],
                'airline3': ['+8615109876543'],
                'airline4': ['+8613554321098'],
                'airline5': ['+8613123456789']
            }

            # customer account
            if user.balance >= amount:
                user.balance -= amount
                user.save()
                # new statement
                statement_data = {
                    'description': airline,
                    'price': amount,
                    'status': False,
                    'user': user,
                }
                statement = Statement.objects.create(**statement_data)
                # airline account
                airline_username = airline_dictionary[airline][0]
                print(airline_username)
                airline_account = CustomUser.objects.get(username=airline_username)
                airline_account.balance += amount
                airline_account.save()
                # new statement
                statement_data = {
                    'description': airline,
                    'price': amount,
                    'status': True,
                    'user': airline_account,
                }
                statement = Statement.objects.create(**statement_data)
                return Response({'orderId': orderId, 'key': key})
            else:
                return Response({'errors': 'Not enough balance'})
        else:
            return Response({'result': 'fail'})