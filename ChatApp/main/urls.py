from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_user, name='signup'),
    path('', views.login_user, name='login'),
    path('dashboard/<username>/', views.user_dashboard, name='user_dashboard'),
    path('logout_user/', views.logout_user, name='logout_user')
    ]