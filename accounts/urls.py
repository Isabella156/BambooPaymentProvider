from django.urls import path
from . import views
from knox.views import LogoutView, LogoutAllView

urlpatterns = [
    path('signup/', views.CreateUserAPI.as_view()),
    path('signin/', views.SigninAPIView.as_view()),
    path('signout/', LogoutView.as_view()),
    path('signout-all/', LogoutAllView.as_view()),
    path('deposit/', views.DepositView.as_view()),
    path('invoice/', views.InvoiceView.as_view()),
    path('pay/', views.PayView.as_view()),
]
