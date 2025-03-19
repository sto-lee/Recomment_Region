from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_view, name='community'),
    path('writepost/', views.writepost_view, name='writepost'),
    path('comment/', views.comment_view, name='comment'),
]