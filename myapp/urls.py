from django.urls import path
from . import views

urlpatterns = [
    path('repay-loan/', views.repay_loan, name='repay_loan'),
    path('loan-repayment/', views.loan_repayment_page, name='loan_repayment_page'),
]