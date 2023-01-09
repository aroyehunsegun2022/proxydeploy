from django.contrib.sites.shortcuts import get_current_site 
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import generics
from rest_framework import views
from rest_framework import status 
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from project_backend import utils 
from project_backend.authentications import serializers
from project_backend import models
from project_backend.authentications.utils import AuthNotificationFacotory

class RegisterView(generics.GenericAPIView):
    '''
    A class that registers a new User
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.RegisterSerializer
    
    def post(self, request):
        data = request.data 
        serializer_data = self.serializer_class(data=data)
        if serializer_data.is_valid(raise_exception=True):
            serializer_data.save()
            
            # send email notification and link for account activation
            user = models.User.objects.get(email=serializer_data.data['email'])
            token = RefreshToken.for_user(user).access_token
            domain_name = get_current_site(request).domain
            abs_path = reverse('verify-email')     
            AuthNotificationFacotory().register_email_notification(domain_name,user,token,abs_path)
            return utils.CustomResponse.Success('Registered Sucessfully', status=status.HTTP_201_CREATED)
        return utils.CustomResponse.Failure(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmail(views.APIView):
    '''
    A view that verifies a user email and set user.is_verified attribute to True
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.VerifyEmailSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Input Your Token', type=openapi.TYPE_STRING)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.query_params.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms=['HS256'])
            user = models.User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return utils.CustomResponse.Success("Successfully Activated", status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as e:
            return utils.CustomResponse.Failure("Activation Link Expired", status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            return utils.CustomResponse.Failure("Invalid Token", status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(generics.GenericAPIView):
    '''
    A view that authenticates a user and return a token
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.LoginSerializer
    
    def post(self, request):
        serializer_data = self.serializer_class(data=request.data)
        if serializer_data.is_valid(raise_exception=True):
            return utils.CustomResponse.Success(serializer_data.data, status=status.HTTP_200_OK)
        return utils.CustomResponse.Failure(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetRequest(generics.GenericAPIView):
    '''
    Password Reset Request View
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordResetRequestSerializer
    
    def post(self, request):
        serializer_data = self.serializer_class(data=request.data)
        if serializer_data.is_valid(raise_exception=True):
            email = serializer_data.validated_data['email']
            try:
                user = models.User.objects.get(email=email)
            except:
                raise NotFound('Inactive User or User Does Not Exist.')
            if not user.is_active:
                return utils.CustomResponse.Failure("Inactive User")
            # encode user object and create a password reset token for user
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            domain_name = get_current_site(request).domain
            abs_path = reverse('password_reset_confirm', kwargs={'uidb64':uidb64, 'token':token})
            AuthNotificationFacotory.send_password_reset_email(domain_name,abs_path,user)
            return utils.CustomResponse.Success("A Password Reset Link has been sent to your Email", status=status.HTTP_200_OK)
            
class PasswordResetConfirm(generics.GenericAPIView):
    '''
    Password Reset Request View Confirmation
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordResetRequestSerializer
    
    def get(self, request, uidb64, token):
        # decode user token and check if valid
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user,token):
                return utils.CustomResponse.Failure("Verification Token is Invalid or Expired", status=status.HTTP_401_UNAUTHORIZED)
            
            payload = {
                'uidb64': uidb64,
                'token': token
            } 
            return utils.CustomResponse.Success(payload, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as e:
            return utils.CustomResponse.Failure("Token not Valid", status=status.HTTP_400_BAD_REQUEST)
        
class PasswordChange(generics.GenericAPIView):
    '''
    A view that updates users password if token is valid
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordChangeSerializer 
    
    def patch(self, request):
        serializer_data = self.serializer_class(data=request.data)
        if serializer_data.is_valid(raise_exception=True):
            return utils.CustomResponse.Success("Password Reset Done", status=status.HTTP_200_OK)
        return utils.CustomResponse.Failure(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(generics.GenericAPIView):
    
    serializer_class = serializers.LogoutSerializer 
    
    def post(self, request):
        data = request.data 
        serializer_data = self.serializer_class(data=data)
        if serializer_data.is_valid(raise_exception=True):
            serializer_data.save()
            return utils.CustomResponse.Success("Logged Successfully", status=status.HTTP_204_NO_CONTENT)
        return utils.CustomResponse.Failure(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)
            
                
            
    