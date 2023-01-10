from rest_framework import generics 
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from project_backend import models
from project_backend.users import serializers
from project_backend import utils
from project_backend.users.utils import IsAdmin
from project_backend.permissions import IsActiveVerifiedAuthenticated

# User Profile Details
class UserProfile(generics.GenericAPIView):
    '''
    A class that fetches user profile based on current request user
    '''
    serializer_class =serializers.UserDetailSerializer
    
    def get(self, request):
        try:
            user = models.User.objects.get(id=request.user.id)
            payload = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phoneNumber": user.phoneNumber,
                "address": user.address,
                "city": user.city,
                "lga": user.lga,
                "state": user.state,
                "user_type": user.user_type
            }
            return utils.CustomResponse.Success(payload, status=status.HTTP_200_OK)
        except:
            user = None

# User update profile details    
class UserUpdateProfile(generics.UpdateAPIView):
    '''
    A class that aloows users update their profile details
    '''
    serializer_class = serializers.UpdateUserDetailSerializer
    queryset = models.User.objects.all()
    lookup_field = 'pk'
    
    def perform_update(self, serializer):
        instance = serializer.save()
        # send mail or push notification to user
        # send_email_confirmation(user=self.request.user, modified=instance)
        
# Admin section to manage user profile
class ListUsers(generics.ListAPIView):
    '''
    A class that list all users in the database (excluding users classified as admins).
    Allows access only to admin users.
    '''
    permission_classes = [IsActiveVerifiedAuthenticated, IsAdmin]
    queryset = models.User.objects.all()
    serializer_class = serializers.ListUsersSerializer
    
    def get_queryset(self):
        return self.queryset.exclude(is_staff=True)
    
class ListUserDetails(generics.RetrieveDestroyAPIView):
    '''
    A class that list and delete an individual user (excluding users classified as admins)
    Allows access only to admin users.
    '''
    permission_classes = [IsActiveVerifiedAuthenticated, IsAdmin]
    queryset = models.User.objects.all()
    serializer_class = serializers.ListUsersSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        return self.queryset.exclude(is_staff=True)
  
     
        