from django.urls import path 

from project_backend.users import views 

urlpatterns = [
    path('profile/', views.UserProfile.as_view(), name='profile'),
    path('<int:pk>/profile/', views.UserUpdateProfile.as_view(), name='user_update_profile'),
    path('admin/users/', views.ListUsers.as_view(), name='list-users'),
    path('admin/user/<int:pk>/', views.ListUserDetails.as_view(), name='user-detail')
]