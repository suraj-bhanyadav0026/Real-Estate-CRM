from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAuthenticatedCustom, IsAdminOrManager, IsAgentOrHigher
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, CustomUserSerializer, LeadSerializer
from .models import Lead, CustomUser
from django.contrib.auth import authenticate
from .permissions import IsOwnerOrAdmin

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role
                }
            })
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': CustomUserSerializer(user).data
        }, status=201)
    return Response({'errors': serializer.errors}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def me_view(request):
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)


# Leads Module 1
@api_view(['GET', 'POST'])
@permission_classes([IsAgentOrHigher])
def lead_list_create(request):
    if request.method == 'GET':
        queryset = Lead.objects.all()
        if request.user.role == 'agent':
            queryset = queryset.filter(assigned_to=request.user)
        serializer = LeadSerializer(queryset, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = LeadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAgentOrHigher, IsOwnerOrAdmin])
def lead_detail(request, pk):
    try:
        lead = Lead.objects.get(pk=pk)
    except Lead.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.user.role == 'agent' and lead.assigned_to != request.user:
        return Response({'error': 'Not your lead'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = LeadSerializer(lead)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = LeadSerializer(lead, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        lead.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
@permission_classes([IsAdminOrManager])
def lead_assign(request, pk):
    try:
        lead = Lead.objects.get(pk=pk)
    except Lead.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    assigned_to_id = request.data.get('assigned_to')
    if assigned_to_id:
        try:
            user = CustomUser.objects.get(id=assigned_to_id)
            lead.assigned_to = user
            lead.save()
            serializer = LeadSerializer(lead)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'assigned_to required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAgentOrHigher])
def lead_status_update(request, pk):
    try:
        lead = Lead.objects.get(pk=pk)
    except Lead.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.user.role == 'agent' and lead.assigned_to != request.user:
        return Response({'error': 'Not your lead'}, status=status.HTTP_403_FORBIDDEN)
    
    status = request.data.get('status')
    if status in dict(Lead.LEAD_STATUS_CHOICES):
        lead.status = status
        lead.save()
        serializer = LeadSerializer(lead)
        return Response(serializer.data)
    return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

