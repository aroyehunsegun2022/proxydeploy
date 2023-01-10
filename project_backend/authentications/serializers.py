from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers 
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from project_backend import models 

class RegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = models.User 
        fields = ['id','first_name','last_name','email','password']
        
    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)
    
class VerifyEmailSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255)
    
    class Meta:
        model = models.User
        fields = ['token']

class LoginSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(min_length=6, write_only=True)
    tokens = serializers.CharField(read_only=True, max_length=200)
    user_access = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = models.User
        fields = ['email','user_access','password','tokens']
        
    def get_user_access(self, obj):
        try:
            access_type = models.User.objects.get(email=obj['email']).user_type
        except:
            access_type = None
        return access_type
    
    def validate(self, attrs):
        email = attrs.get('email', None)
        password = attrs.get('password', None)
        
        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid Login Credentials")
        if not user.is_verified:
            raise AuthenticationFailed("Email is Not Verified")
        if not user.is_active:
            raise AuthenticationFailed("Account Disabled, Contact the Administrator")
        
        return {
            'email': user.email,
            'tokens': user.tokens
        }
        
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    class Meta:
        fields = ['email']
        
class PasswordChangeSerializer(serializers.Serializer):
    
    password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    
    class Meta:
        fields = ['password','token','uidb64']
        
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            
            id = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise AuthenticationFailed("Verification Token is invalid or Expired", 401)
            
            user.set_password(password)
            user.save()
            return user 
        except Exception as e:
            raise AuthenticationFailed("Verification Token is invalid or Expired", 401)

class LogoutSerializer(serializers.Serializer):
    
    refresh = serializers.CharField()
    default_error_message = {
        'bad_token': ('Token is Expired or Invalid')
    }
    
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist() 
        except TokenError:
            self.fail("bad_token")
        return super().save(**kwargs)