# analisis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_analisis, name='dashboard_analisis'),
    path('reporte-financiero/', views.reporte_financiero, name='reporte_financiero'),
]