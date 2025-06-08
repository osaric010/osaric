"""
URL configuration for osaric_accounts project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from core.search_views import global_search, search_suggestions

def redirect_to_dashboard(request):
    return redirect('dashboard:home')

def multilevel_dropdowns_demo(request):
    return render(request, 'demo/multilevel_dropdowns.html', {
        'title': 'القوائم المنبثقة السهلة الاستخدام'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('definitions/', include('definitions.urls')),
    path('sales/', include('sales.urls')),
    path('purchases/', include('purchases.urls')),
    path('inventory/', include('inventory.urls')),
    path('treasury/', include('treasury.urls')),
    path('assets/', include('assets.urls')),
    path('hr/', include('hr.urls')),
    path('reports/', include('reports.urls')),
    path('branches/', include('branches.urls')),
    path('accounting/', include('accounting.urls')),
    path('services/', include('services.urls')),
    path('windows/', include('windows.urls')),
    path('demo/multilevel-dropdowns/', multilevel_dropdowns_demo, name='multilevel_dropdowns_demo'),

    # Global Search API
    path('api/global-search/', global_search, name='global_search'),
    path('api/search-suggestions/', search_suggestions, name='search_suggestions'),

    path('', redirect_to_dashboard, name='home'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
