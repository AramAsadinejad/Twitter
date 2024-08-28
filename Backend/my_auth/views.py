from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserCreateSerializer,UserLoginSerializer,TweetSerializer
from .models import User,Tweet
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404


class Home(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
    
class UserCreateView(APIView):
    permission_classes = [AllowAny]
    # authentication_classes = [JWTAuthentication]
    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    # authentication_classes = [JWTAuthentication]
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TweetView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, tweet_id=None):
        if tweet_id:
            try:
                tweet = Tweet.objects.get(id=tweet_id)
                serializer = TweetSerializer(tweet)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Tweet.DoesNotExist:
                return Response({"detail": "Tweet not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            tweets = Tweet.objects.all()
            serializer = TweetSerializer(tweets, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = TweetSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            tweet = Tweet.objects.get(id=request.data.get("id"), user=request.user)
            tweet.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Tweet.DoesNotExist:
            return Response({"detail": "Tweet not found or you do not have permission to delete this tweet."}, status=status.HTTP_404_NOT_FOUND)

class FollowView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id)
            if user_to_follow == request.user:
                return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
            
            if request.user.followings.filter(id=user_id).exists():
                return Response({"detail": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)
            
            request.user.followings.add(user_to_follow)
            user_to_follow.followers.add(request.user)
            return Response({"detail": "You are now following this user."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id):
        try:
            user_to_unfollow = User.objects.get(id=user_id)
            if not request.user.followings.filter(id=user_id).exists():
                return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)
            
            request.user.followings.remove(user_to_unfollow)
            user_to_unfollow.followers.remove(request.user)
            return Response({"detail": "You have unfollowed this user."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class LikeTweetView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        tweet_id=request.data.get("id")
        tweet = get_object_or_404(Tweet, id=tweet_id)
        user = request.user

        if user in tweet.likes.all():
            tweet.likes.remove(user)
            action = 'unliked'
        else:
            tweet.likes.add(user)
            action = 'liked'

        tweet.save()
        return Response({'status': f'Tweet {action}'}, status=status.HTTP_200_OK)
    
class CommentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, tweet_id):
        parent_tweet = get_object_or_404(Tweet, id=tweet_id)
        
        data = request.data.copy()
        data['parent'] = tweet_id
        serializer = TweetSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            comment = serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)