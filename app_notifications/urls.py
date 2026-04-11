# notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification-list'),
    path('<int:pk>/read/', views.mark_as_read, name='notification-read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark-all-read'),
    path('unread-count/', views.unread_count, name='unread-count'),
]