from django.urls import path, include

urlpatterns = [
    path('auth/', include('project_backend.authentications.urls')),
]