"""
URL configuration for products_service project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from products.auth_views import login, test_users

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('products.urls')),
    path('api/auth/login/', login, name='login'),
    path('api/auth/test-users/', test_users, name='test-users'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

