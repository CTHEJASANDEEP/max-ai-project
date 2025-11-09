from django.urls import path
from . import views  # '.' means "from this same folder"

urlpatterns = [
    # Main page
    path('', views.index, name='index'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # NEW: Chat and History
    path('new_chat/', views.new_chat, name='new_chat'),
    path('clear_history/', views.clear_history, name='clear_history'),
]