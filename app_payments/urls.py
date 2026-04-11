from django.urls import path
from app_payments import views

urlpatterns = [    
    path('payment/', views.payment, name='payment'),
]