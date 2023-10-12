from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    AuthUserSerializer,
    UserRegistrationSerializer,
    ProfileSerializers,
    AvatarUpdateSerializer
)
from .models import Profile


class SignIn(GenericAPIView):
    """
    APIView класс осуществляет вход пользователей
    """
    serializer_class = AuthUserSerializer

    @extend_schema(tags=['auth'], description='Sign in')
    def post(self, request: Request, *args, **kwargs) -> Response:
        print('Start POST')
        # Получение данных из запроса
        try:
            request_data = json.loads(list(request.data.keys())[0])
            username = request_data.get('username')
            password = request_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Аутентификация успешна, выполняем вход пользователя
                login(request, user)
                return Response({'message': 'Authenticated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Error processing request'}, status=status.HTTP_400_BAD_REQUEST)


class SignOut(GenericAPIView):
    """
        APIView класс осуществляет выход пользователя из системы
    """
    serializer_class = AuthUserSerializer

    @extend_schema(tags=['auth'], description='Sign out')
    def post(self, request: Request) -> Response:
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


class SignUp(GenericAPIView):
    """
        APIView класс осуществляет регистрацию пользователя
    """
    serializer_class = UserRegistrationSerializer

    def post(self, request: Request) -> Response:
        request_data = json.loads(list(request.data.keys())[0])
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid():
            user = serializer.save()
            # Вход в систему созданного пользователя
            login(request, user)
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileUser(GenericAPIView):
    """
        APIView класс создает профиль пользователя
        update_profile - создание/обновление данных профиля
        change_password - смена пароля
    """
    serializer_class = ProfileSerializers

    def post(self, request):
        data = request.data
        if 'newPassword' in data:
            return self.change_password(request, data['newPassword'])
        else:
            return self.update_profile(request, data)

    def get(self, request: Request) -> Response:

        if request.user.is_authenticated:  # Проверяем, аутентифицирован ли пользователь
            profile, created = Profile.objects.get_or_create(user=request.user)
            serializer = ProfileSerializers(profile)
            alt_name = f'user_{request.user.username}_{profile.pk}'  # Включаем username и pk
            data = serializer.data

            data['avatar'] = {
                "src": data['avatar'],
                "alt": alt_name,
            }

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    def update_profile(self, request, profile_data):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializers(profile, data={
            'fullName': profile_data.get('fullName', profile.fullName),
            'phone': profile_data.get('phone', profile.phone),
            'email': profile_data.get('email', profile.email),
        }, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def change_password(self, request, new_password):
        if request.user.is_authenticated:
            user = request.user
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


class AvatarUpdateView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = AvatarUpdateSerializer(data=request.data)

        if serializer.is_valid():
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.avatar = serializer.validated_data['avatar']
            profile.save()

            return Response({'message': 'Avatar updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

