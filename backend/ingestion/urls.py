from django.urls import path
from . import views

urlpatterns = [
    path('batches/', views.batches_list),
    path('raw-records/', views.raw_records_list),
    path('normalized/', views.normalized_list),
    path('audit-logs/',views.audit_logs_list),
    path('approve/<int:pk>/', views.approve_activity),
    path('reject/<int:pk>/', views.reject_activity),
]