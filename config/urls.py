from django.contrib import admin
from django.urls import path, include
from login.views import kakao_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('base/', include('base.urls')),
    path('community/', include('community.urls')),
    path('listings/', include('listings.urls')),
    path('login/', include('login.urls')),
    path('mypage/', include('mypage.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('auth/kakao/callback/', kakao_callback, name='kakao_callback'),
    path("__reload__/", include("django_browser_reload.urls")),
]
