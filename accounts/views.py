from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    UserSerializer(user).data,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'message': 'Registration pending admin approval.' if user.role == 'doctor' else 'Registration successful.',
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email    = request.data.get('email')
    password = request.data.get('password')
    role     = request.data.get('role')

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(username=user_obj.username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.role != role:
        return Response({'error': f'This account is not registered as {role}'}, status=status.HTTP_403_FORBIDDEN)

    if not user.is_approved:
        return Response({
            'error': 'Account pending admin approval',
            'is_approved': False,
        }, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    return Response({
        'user':    UserSerializer(user).data,
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


# ── Admin only endpoints ──────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_doctors(request):
    doctors = User.objects.filter(role='doctor', is_approved=False)
    return Response(UserSerializer(doctors, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_doctor(request, user_id):
    doctor = get_object_or_404(User, id=user_id, role='doctor')
    doctor.is_approved = True
    doctor.save()
    return Response({
        'message': f'Dr. {doctor.get_full_name()} approved successfully.',
        'user': UserSerializer(doctor).data,
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_doctor(request, user_id):
    doctor = get_object_or_404(User, id=user_id, role='doctor')
    doctor.is_approved = False
    doctor.save()
    return Response({
        'message': f'Dr. {doctor.get_full_name()} rejected.',
        'user': UserSerializer(doctor).data,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_users(request):
    users = User.objects.all().order_by('-date_joined')
    return Response(UserSerializer(users, many=True).data)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    if request.user.id == user_id:
        return Response(
            {'error': 'You cannot delete your own account.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return Response(
        {'message': f'User {user.email} deleted successfully.'},
        status=status.HTTP_200_OK
    )