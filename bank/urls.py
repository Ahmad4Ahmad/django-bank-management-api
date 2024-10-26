from django.urls import path
from .views import GrantLoanView, LoanRepaymentView, GetCustomerLoansView

urlpatterns = [
    path('loans/grant/', GrantLoanView.as_view(), name='grant-loan'),
    path('loans/repay/<int:pk>/', LoanRepaymentView.as_view(), name='repay-loan'),
    path('loans/', GetCustomerLoansView.as_view(), name='get-loans'),
]