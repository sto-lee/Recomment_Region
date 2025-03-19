from django.urls import path
from . import views

urlpatterns = [
    path('', views.mypage_view, name='mypage'),
    path('profile/', views.myprofile_view, name='myprofile'),
    path('bookmarks/', views.mybookmarks_view, name='mybookmarks'),
    path('posts/', views.myposts_view, name='myposts'),
]