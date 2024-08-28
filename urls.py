from django.urls import path
from system import admin
from . import views
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView
from django.contrib.auth import views as auth_views
from .views import get_universities

app_name = 'system'
urlpatterns = [
    path('', views.home, name = 'homepage'),
    path('Blog1/', views.Blog1, name='Blog1'),
    path('Blog2/', views.Blog2, name='Blog2'),
    path('Blog3/', views.Blog3, name='Blog3'),
    path('Blog4/', views.Blog4, name='Blog4'),
    path('Blog5/', views.Blog5, name='Blog5'),
    path('Sign_in/', views.custom_login_view, name='signin'),
    path('Sign_in/', views.Sign_in, name='Sign_in'),
    path('admin/register/', views.admin_register, name='admin_register'),  # New URL for admin registration
    path('register/', views.admin_register, name='register'),
    path('login/', views.user_login, name = 'login'),

    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   
    path('main_sys/', views.main_view, name='main_sys'),
    path('universities/', views.university_list, name='university_list'),
    path('results/', views.filter_university, name='filter_university'),
    path('get_universities/', views.get_universities, name='get_universities'),

    path('logout/', views.logout_view, name='logout'),

    path('preferences/', views.preference_view, name='preferences'),
    path('major-autocomplete/', views.major_autocomplete, name='major_autocomplete'),
]
