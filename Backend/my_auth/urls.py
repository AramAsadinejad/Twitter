from django.urls import path
from .views import Home,UserCreateView,UserLoginView,FollowView,TweetView,LikeTweetView,CommentView


urlpatterns = [
    path('', Home.as_view()),
    path('signup/', UserCreateView.as_view(), name='user-signup'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('follow/<int:user_id>/', FollowView.as_view(), name='follow-unfollow'),
    path('tweet/',TweetView.as_view(),name='tweet'),
    path('tweet/<int:tweet_id>/like/', LikeTweetView.as_view(), name='like-tweet'),
    path('tweet/<int:tweet_id>/comment/', CommentView.as_view(), name='comment-tweet'),
]