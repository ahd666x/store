from django.urls import path
from . import views

app_name = 'communications'
urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
]
