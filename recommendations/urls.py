from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # 구/동 정보 API
    path('get_districts/', views.get_districts, name='get_districts'),
    path('get_dongs/', views.get_dongs, name='get_dongs'),
    
    # 모달용 iframe 경로 추가
    path('modal_page1/', views.modal_page1_view, name='modal_page1'),
    path('modal_page2/', views.modal_page2_view, name='modal_page2'),
    path('modal_page3/', views.modal_page3_view, name='modal_page3'),
    path('modal_confirm/', views.modal_confirm_view, name='modal_confirm'),
    path('modal_result/', views.modal_result_view, name='modal_result'),
    path('recommend/', views.recommend_api, name='recommend_api'),
]