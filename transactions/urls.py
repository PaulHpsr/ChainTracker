from django.urls import path
from .views import transactions_view

urlpatterns = [
    path('', transactions_view, name='transactions_list'),
]
