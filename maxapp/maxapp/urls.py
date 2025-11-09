# Path: max_project/maxapp/urls.py

from django.urls import path
from . import views  # '.' means "from this same folder, import views.py"

urlpatterns = [
    # This maps your homepage (/) to the 'index' function in views.py
    path('', views.index, name='index'), 
    
    # Maps /register/ to the 'register_view' function
    path('register/', views.register_view, name='register'),
    
    # Maps /login/ to the 'login_view' function
    path('login/', views.login_view, name='login'),
    
    # Maps /logout/ to the 'logout_view' function
    path('logout/', views.logout_view, name='logout'),
    
    # Maps /admin_dashboard/ to the 'admin_dashboard' function
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]