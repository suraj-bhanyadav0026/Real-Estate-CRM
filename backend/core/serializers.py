from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'role', 'phone', 'profile_photo', 'specialization', 'is_active_agent')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        validated_data['username'] = validated_data.get('email', '').split('@')[0]  # username from email prefix
        validated_data['role'] = validated_data.get('role', 'agent')
        user = CustomUser.objects.create_user(**validated_data)
        return user

from rest_framework import serializers
from .models import Lead
from django.core.exceptions import ValidationError
from django.contrib.auth.models import CustomUser  # Already imported? No, from .models

class LeadSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Lead
        fields = ('id', 'name', 'phone', 'email', 'budget_min', 'budget_max', 'location_pref', 'property_type_pref', 'source', 'notes', 'status', 'score', 'assigned_to', 'created_at', 'updated_at')
        read_only_fields = ('id', 'score', 'created_at', 'updated_at')
    
    def validate(self, data):
        # Duplicate check
        phone = data.get('phone')
        email = data.get('email')
        if Lead.objects.filter(phone=phone, email__iexact=email or '').exclude(id=self.instance.id if self.instance else None).exists():
            raise ValidationError('Lead with this phone/email already exists.')
        # Manager assign only
        assigned_to = data.get('assigned_to')
        if assigned_to and self.context['request'].user.role not in ['admin', 'manager']:
            raise ValidationError('Only admins/managers can assign leads.')
        return data

    def create(self, validated_data):
        return super().create(validated_data)

