from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.models import UserProfile


class UserDetailSerializer(serializers.ModelSerializer):
    """Read-only serializer returning id, email, and fullname for a user."""

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """Return the best available display name for the user."""
        if hasattr(obj, 'userprofile') and obj.userprofile.fullname:
            return obj.userprofile.fullname
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the UserProfile model including related user fields."""

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'fullname', 'username', 'email']


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate and create a new user account."""

    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """Ensure passwords match and the email is not already taken."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
        return data

    def save(self):
        """Create and persist the user account with its profile."""
        fullname = self.validated_data['fullname']
        email = self.validated_data['email']
        password = self.validated_data['password']
        account = User(email=email, username=email)
        account.set_password(password)
        account.save()
        profile = account.userprofile
        profile.fullname = fullname
        profile.save()
        return account


class LoginSerializer(serializers.Serializer):
    """Validate email/password credentials and return the authenticated user."""

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate the user and attach the user object to the data."""
        email = data.get('email')
        password = data.get('password')
        if not (email and password):
            raise serializers.ValidationError("Must include 'email' and 'password'.")
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        data['user'] = user
        return data


class EmailCheckSerializer(serializers.Serializer):
    """Validate that an email field is present and correctly formatted."""

    email = serializers.EmailField(required=True)
