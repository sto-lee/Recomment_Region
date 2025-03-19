from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('kakao/', views.kakao_login, name='kakao_login'),
    path('kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('logout/', views.logout_view, name='logout'),
]