from django.urls import path
from . import views
from knox.views import LogoutView, LogoutAllView

urlpatterns = [
    path('signup/', views.CreateUserAPI.as_view(), name='signup'),
    path('signin/', views.SigninAPIView.as_view(), name='signin'),
    path('signout/', LogoutView.as_view(), name='signout'),
    path('signout-all/', LogoutAllView.as_view(), name='signout_all'),
    path('deposit/', views.DepositView.as_view(), name='deposit'),
    path('invoice/', views.InvoiceView.as_view(), name='invoice'),
    path('pay/', views.PayView.as_view(), name='pay'),
    path('transfer/', views.TransferView.as_view(), name='transfer'),
    path('balance/', views.BalanceView.as_view(), name='balance'),
    path('statement/', views.StatementView.as_view(), name='statement'),
]
