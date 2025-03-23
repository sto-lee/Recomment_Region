from django.urls import path, include

urlpatterns = [
    path('', include('listings.urls')),
    path('recommendations/', include('recommendations.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]
