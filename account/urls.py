from django.urls import path
from .views import (
    CreateAccountView,
    DepositView,
    WithdrawView,
    SuspendAccountView,
    CloseAccountView,
    TransferView,
    UserTransactionsView
)

urlpatterns = [
    path('create/', CreateAccountView.as_view(), name='account-create'),
    path('deposit/<int:pk>/', DepositView.as_view(), name='account-deposit'),
    path('withdraw/<int:pk>/', WithdrawView.as_view(), name='account-withdraw'),
    path('suspend/<int:pk>/', SuspendAccountView.as_view(), name='account-suspend'),
    path('close/<int:pk>/', CloseAccountView.as_view(), name='account-close'),
    path('transfer/', TransferView.as_view(), name='account-transfer'),
    path('transactions/', UserTransactionsView.as_view(), name='user-transactions')
]
