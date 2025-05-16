from django.urls import path
from .views import portfolio_dashboard, add_wallet, delete_wallet

urlpatterns = [
    path('', portfolio_dashboard, name='portfolio_dashboard'),
    path('add/', add_wallet, name='add_wallet'),
    path('delete/<int:pk>/', delete_wallet, name='delete_wallet'),
]
