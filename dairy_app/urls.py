from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-milk/', views.add_milk, name='add_milk'),
    path('slip/<int:pk>/', views.download_slip, name='download_slip'),
    path('ledger/', views.farmer_ledger, name='farmer_ledger'),
    path('pay-farmer/<int:farmer_id>/', views.pay_farmer, name='pay_farmer'),
    path('payment-slip/<int:farmer_id>/', views.download_payment_slip, name='download_payment_slip'),
]