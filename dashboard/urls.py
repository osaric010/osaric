from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('currency-rates/', views.currency_rates_widget, name='currency_rates'),
    path('currency-rates/full/', views.currency_rates_full, name='currency_rates_full'),
    path('update-currency-rates/', views.update_currency_rates_ajax, name='update_currency_rates'),
]
