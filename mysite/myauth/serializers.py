from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "profile"]

    profile = serializers.SerializerMethodField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'password']


class ProfileSerializers(serializers.ModelSerializer):

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            avatar_url = obj.avatar.url
            full_url = request.build_absolute_uri(avatar_url)
            user_pk = obj.user.pk if obj.user else ''  # Получаем pk пользователя из профиля
            alt_name = f'user_{user_pk}'
            return {
                'src': full_url,
                'alt': alt_name
            }
        return None

    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']


class ProfileOrderSerializers(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['fullName', 'phone', 'email']


class ProfileUploadAvatarSerializer(serializers.ModelSerializer):
    model = Profile
    fields = ["user", "avatar"]


class AvatarUpdateSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

