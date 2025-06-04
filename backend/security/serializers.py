from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                message='Password must contain at least 8 characters including letters, numbers, and special characters'
            )
        ]
    )
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'phone_number', 'date_of_birth'
        ]

    def validate(self, data):
        # Password confirmation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })

        # Age validation (must be at least 18)
        if data.get('date_of_birth'):
            today = date.today()
            age = (today.year - data['date_of_birth'].year -
                  ((today.month, today.day) <
                   (data['date_of_birth'].month, data['date_of_birth'].day)))
            if age < 18:
                raise serializers.ValidationError({
                    'date_of_birth': 'You must be at least 18 years old'
                })

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    ip_address = serializers.IPAddressField(required=False)

    def validate(self, data):
        user = None
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'username': 'No account found with this username'
            })

        # Check if account is locked
        if user.is_account_locked():
            lock_time = user.account_locked_until - timezone.now()
            minutes = round(lock_time.total_seconds() / 60)
            raise serializers.ValidationError({
                'non_field_errors': f'Account is locked. Try again in {minutes} minutes'
            })

        return data

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'profile_image',
            'role', 'kyc_status', 'two_factor_enabled'
        ]
        read_only_fields = ['username', 'role', 'kyc_status']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        min_length=8,
        style={'input_type': 'password'},
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                message='Password must contain at least 8 characters including letters, numbers, and special characters'
            )
        ]
    )
    confirm_new_password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({
                'confirm_new_password': 'Passwords do not match'
            })
        return data