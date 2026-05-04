from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth.models import User
from .serializers import RegistrationSerializer, LoginSerializer, EmailCheckSerializer

class RegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        token, create = Token.objects.get_or_create(user=account)
        return Response({
            'user_id': account.id,
            'fullname': serializer.validated_data['fullname'],
            'email': account.email,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
        data = request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user_id': user.id,
            'fullname': user.userprofile.fullname,
            'email': user.email,
            'token': token.key
        })

class EmailCheckView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailCheckSerializer

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email')
        
        serializer = self.get_serializer(data={'email': email})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            return Response({
                "user_id": user.id,
                "fullname": user.userprofile.fullname,
                "email": user.email
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)