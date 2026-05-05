from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import EmailCheckSerializer, LoginSerializer, RegistrationSerializer


class RegistrationView(generics.CreateAPIView):
    """Create a new user account and return an authentication token."""

    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        """Validate registration data, save the user, and return token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        token, _ = Token.objects.get_or_create(user=account)
        return Response({
            'user_id': account.id,
            'fullname': serializer.validated_data['fullname'],
            'email': account.email,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    """Authenticate a user by email and password and return a token."""

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """Validate credentials and return the user's auth token."""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user_id': user.id,
            'fullname': user.userprofile.fullname,
            'email': user.email,
            'token': token.key
        })


class EmailCheckView(generics.GenericAPIView):
    """Check whether a given email address belongs to an existing user."""

    permission_classes = [IsAuthenticated]
    serializer_class = EmailCheckSerializer

    def get(self, request, *args, **kwargs):
        """Return basic user data for the given email or 404."""
        email = request.query_params.get('email')
        self.get_serializer(data={'email': email}).is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=email)
            return Response(
                {'id': user.id, 'fullname': user.userprofile.fullname, 'email': user.email}
            )
        except User.DoesNotExist:
            return Response({'message': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)


class LogoutView(generics.GenericAPIView):
    """Delete the current user's authentication token to log them out."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Delete the auth token and confirm logout."""
        request.auth.delete()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
