from django.urls import path
from . import views

app_name = 'production'
urlpatterns = [
    path('tasks/', views.ProductionTaskListView.as_view(), name='task_list'),
    path('kanban/', views.ProductionKanbanView.as_view(), name='kanban'),
    path('report/', views.ProductionReportView.as_view(), name='report'),
    path('workers/', views.WorkerListView.as_view(), name='worker_list'),
    path('holidays/', views.HolidayListView.as_view(), name='holiday_list'),
    path('painting-processes/', views.PaintingProcessListView.as_view(), name='painting_process_list'),
]
