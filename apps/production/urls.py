from django.urls import path
from . import views

app_name = 'production'
urlpatterns = [
    path('tasks/', views.ProductionTaskListView.as_view(), name='task_list'),
]
