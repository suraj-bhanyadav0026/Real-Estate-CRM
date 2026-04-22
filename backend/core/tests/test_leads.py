import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Lead, CustomUser
from django.urls import reverse

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user():
    return CustomUser.objects.create_superuser(email='admin@test.com', password='pass')

@pytest.fixture
def agent_user():
    return CustomUser.objects.create_user(email='agent@test.com', password='pass', role='agent')

@pytest.fixture
def manager_user():
    return CustomUser.objects.create_user(email='manager@test.com', password='pass', role='manager')

@pytest.mark.django_db
class TestLeads:
    def test_create_lead(self, api_client, admin_user):
        api_client.force_authenticate(admin_user)
        data = {
            'name': 'Test Lead',
            'phone': '+1234567890',
            'budget_min': 1000000,
            'source': 'website'
        }
        response = api_client.post('/api/leads/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['score'] >= 50  # Auto score

    def test_duplicate_lead(self, api_client, admin_user):
        api_client.force_authenticate(admin_user)
        data = {'name': 'Dup', 'phone': '+1234567890', 'source': 'ads'}
        api_client.post('/api/leads/', data)  # Create first
        response = api_client.post('/api/leads/', data)
        assert 'already exists' in str(response.data['non_field_errors'])

    def test_agent_sees_own_leads(self, api_client, agent_user):
        lead = Lead.objects.create(name='Agent Lead', phone='agentphone', assigned_to=agent_user)
        api_client.force_authenticate(agent_user)
        response = api_client.get('/api/leads/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_manager_assign(self, api_client, manager_user, agent_user):
        lead = Lead.objects.create(name='Unassigned', phone='unassign')
        api_client.force_authenticate(manager_user)
        data = {'assigned_to': agent_user.id}
        response = api_client.patch(f'/api/leads/{lead.id}/assign/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['assigned_to']['id'] == agent_user.id

    def test_status_update_agent(self, api_client, agent_user):
        lead = Lead.objects.create(name='Test', phone='test', assigned_to=agent_user, status='new')
        api_client.force_authenticate(agent_user)
        data = {'status': 'contacted'}
        response = api_client.patch(f'/api/leads/{lead.id}/status/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'contacted'

