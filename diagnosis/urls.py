from django.urls import path
from .views import (
    PredictView,
    DoctorReportsView,
    PatientReportsView,
    ScanDetailView,
    PatientListView,
    HealthCheckView,
)

urlpatterns = [
    path('predict/',             PredictView.as_view(),        name='predict'),
    path('health/',              HealthCheckView.as_view(),    name='health'),

    path('doctor/reports/',      DoctorReportsView.as_view(),  name='doctor-reports'),
    path('patients/',            PatientListView.as_view(),    name='patient-list'),
    path('patient/reports/',     PatientReportsView.as_view(), name='patient-reports'),
    path('scans/<int:scan_id>/', ScanDetailView.as_view(),     name='scan-detail'),
]