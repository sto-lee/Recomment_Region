from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.recommendations_view, name='recommend_page_1'),
    path('page2/', views.recommend_view, name='recommend_page_2'),
    path('result/', views.recommend_result_view, name='result_recommend'),
]