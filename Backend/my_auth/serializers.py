from rest_framework import serializers
from .models import User,Hashtag,Tweet
from django.contrib.auth import authenticate,get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'bio', 'website', 'followers_count', 'following_count']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'is_official']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            is_official=validated_data.get('is_official', False),
            
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not (username or email or phone_number):
            raise serializers.ValidationError('Username, email or phone number is required.')

        user = authenticate(username=username, email=email, phone_number=phone_number, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid credentials.')

        return {
            'user': user
        }
    
class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name']



class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    hashtags = HashtagSerializer(read_only=True, many=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    retweet = serializers.PrimaryKeyRelatedField(queryset=Tweet.objects.all(), required=False, allow_null=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Tweet.objects.all(), required=False, allow_null=True)
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)

    class Meta:
        model = Tweet
        fields = ['id', 'user', 'text', 'created_at', 'likes', 'likes_count', 'hashtags', 'retweet','parent', 'replies_count']
        read_only_fields = ['created_at', 'hashtags', 'likes', 'user','replies_count']

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return Tweet.objects.create(**validated_data)

    def validate_text(self, value):
        if not value.strip() and not self.initial_data.get('retweet') and not self.initial_data.get('parent'):
            raise serializers.ValidationError("Tweet text cannot be empty unless it's a retweet or a reply.")
        return value
