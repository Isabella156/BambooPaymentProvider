from .models import CustomUser, Invoice, Statement
from .serializers import SignupUserSerializer, LoginSerializer, UserSerializer, DepositSerializer, InvoiceSerializer, PaySerializer, TransferSerializer, StatementSerializer

from django.shortcuts import render
from django.contrib.auth import login
from django.db import transaction

from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, authentication, generics, permissions
from rest_framework.permissions import AllowAny

from knox import views as knox_views
from knox.auth import TokenAuthentication

import datetime



# TODO: change http response status code

class CustomResponse(Response):
    def __init__(self, code, msg, data, status=None, headers=None):
        content = {'code': code, 'msg': msg, 'data': data}
        super().__init__(data=content, status=status, headers=headers)

class CreateUserAPI(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignupUserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            response_data = serializer.data.copy()
            return CustomResponse('200', 'successful', response_data)
        else:
            response_data = serializer.errors
            return CustomResponse('400', 'fail', response_data)
        

class SigninAPIView(knox_views.LoginView):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
            response = super().post(request, format=None)
            response = response.data
            user = response["user"]
            response.update(user)
            del response["user"]
        else:
            return CustomResponse('400', 'fail', serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return CustomResponse('200', 'successful', response)

class DepositView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = DepositSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        user_id = request.user.id
        if serializer.is_valid(raise_exception=True):
            amount = serializer.validated_data['depositMoney']
            user = CustomUser.objects.get(pk=user_id)
            # deposit money
            user.balance += amount
            user.save()
            balance = user.balance
            
            # new statement
            statement_data = {
                    'description': 'deposit',
                    'price': amount,
                    'status': True,
                    'user': user,
            }
            statement = Statement.objects.create(**statement_data)
            
            response_data = {'userBalance': balance}
            return CustomResponse('200', 'successful', response_data)

class InvoiceView(CreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()

        response_data = serializer.data.copy()
        return CustomResponse('201', 'successful', response_data)

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
            invoiceSet = Invoice.objects.filter(orderId=orderId)
            if invoiceSet.count() > 1:
                return CustomResponse('400', 'fail', 'More than one order to pay', status=status.HTTP_400_BAD_REQUEST)
            else:
                invoice = invoiceSet.first()
                amount = invoice.totalAmount
                airline = getattr(invoice, 'airline')
                key = getattr(invoice, 'key')
                user = CustomUser.objects.get(pk=user_id)

                # airline dictionary
                airline_dictionary = {
                    'boyboy': ['+8618301234567'],
                    'KingAirline': ['+8613507654321'],
                    'CandyAirline': ['+8615109876543'],
                    'Elephant': ['+8613554321098'],
                    'Frank': ['+8613123456789']
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
                    response_data = {'orderId': orderId, 'key': key}
                    return CustomResponse('200', 'successful', response_data)
                else:
                    return CustomResponse('400', 'fail', 'Not enough money', status=status.HTTP_400_BAD_REQUEST)
        else:
            return CustomResponse('400', 'fail', serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransferView(GenericAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = TransferSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        user_id = request.user.id
        if serializer.is_valid(raise_exception=True):
            user = CustomUser.objects.get(pk=user_id)
            amount = serializer.validated_data['transferMoney']
            if user.balance < amount:
                response_data = {'error': 'Not enough money'}
                return CustomResponse('400', 'fail', response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.balance -= amount
                user.save()
                
                payee = CustomUser.objects.get(username=serializer.validated_data['phoneNumber'])
                payee.balance += amount
                payee.save()
                payer_name = user.name
                payee_name = payee.name
                # new statement for payer
                statement_data = {
                    'description': f'transfer to {payee_name}',
                    'price': amount,
                    'status': False,
                    'user': user,
                }
                statement = Statement.objects.create(**statement_data)
                # new statement for payee
                statement_data = {
                    'description': f'transfer from {payer_name} ',
                    'price': amount,
                    'status': True,
                    'user': payee,
                }
                statement = Statement.objects.create(**statement_data)
                response_data = {
                    'transferStatus': "True",
                    'balance': user.balance
                }
                return CustomResponse('200', 'successful', response_data)


class BalanceView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        user = CustomUser.objects.get(pk=user_id)
        response_data = {
            "balance": user.balance
        }
        return CustomResponse('200', 'successful', response_data)

class StatementView(ListAPIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = StatementSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        queryset = Statement.objects.filter(user_id=user_id)
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "statements": serializer.data
        }
        return CustomResponse('200', 'successful', serializer.data)