from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Login route taaki seedha login page khul sake
    path('accounts/login/', LoginView.as_view(template_name='dairy_app/login.html'), name='login'),
    
    # Hamara dairy app ke routes
    path('', include('dairy_app.urls')),
]