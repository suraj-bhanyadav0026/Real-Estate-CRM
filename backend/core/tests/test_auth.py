import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import CustomUser

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user():
    return CustomUser.objects.create_user(
        email='admin@test.com', password='testpass123', role='admin'
    )

@pytest.mark.django_db
def test_register_user(api_client):
    url = reverse('core:register')  # namespace later
    data = {
        'email': 'agent@test.com',
        'password': 'testpass123',
        'first_name': 'John',
        'role': 'agent'
    }
    response = api_client.post('/api/auth/register/', data)
    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(email='agent@test.com').exists()

@pytest.mark.django_db
def test_login_user(api_client, admin_user):
    url = reverse('core:login')
    data = {'email': 'admin@test.com', 'password': 'testpass123'}
    response = api_client.post('/api/auth/login/', data)
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

@pytest.mark.django_db
def test_me_view(api_client, admin_user):
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    response = client.get('/api/auth/me/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'admin@test.com'

@pytest.mark.django_db
def test_register_admin_fails(api_client):  # Non-admin can't register admin
    data = {'email': 'fake@test.com', 'password': 'pass', 'role': 'admin'}
    response = api_client.post('/api/auth/register/', data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Via serializer validation later

