from django.urls import path
from . import views

urlpatterns = [
    path('', views.listings_view, name='listings'),
    path('map/', views.map_view, name='map'),
    path("get_dongs/", views.get_dongs, name="get_dongs"),
    # path('save_clusters/', views.save_clusters, name='save_clusters'), # 클러스터 저장
]