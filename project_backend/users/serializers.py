from rest_framework import serializers 

from project_backend import models 

class UserDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.User
        fields = ['id','first_name','last_name','phoneNumber','address','city','lga','state']
    
class UpdateUserDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.User
        fields = ['first_name','last_name','phoneNumber','address','city','lga','state']
        
class ListUsersSerializer(serializers.ModelSerializer):
    
    user_link = serializers.HyperlinkedIdentityField(
        view_name= 'user-detail',
        lookup_field = 'pk'
    )
    class Meta:
        model = models.User
        fields = ['id','first_name','last_name','phoneNumber','address','city','lga','state','user_link','is_verified','is_active']
    