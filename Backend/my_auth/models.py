from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import ValidationError

# Create your models here.

class User(AbstractUser):
    bio=models.TextField(max_length=200,blank=True,null=True)
    phone_number=models.CharField(max_length=100,unique=True,blank=True, null=True)
    email=models.EmailField(unique=True,blank=True, null=True)
    is_official=models.BooleanField(default=False)
    #profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='followings', blank=True)
    website = models.URLField(blank=True, null=True)
    def clean(self):
        if not self.email and not self.phone_number:
            raise ValidationError('Either email or phone number must be provided.')
        super().clean()

class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Tweet(models.Model):
    text=models.CharField(max_length=500)
    #image=models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    user=models.ForeignKey(to=User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    retweet = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='retweets')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    comments = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL,related_name='commented')
    likes = models.ManyToManyField(User, related_name='liked_tweets', blank=True)
    hashtags = models.ManyToManyField(Hashtag, related_name='tweets', blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_reply(self):
        return self.parent is not None
    
    @property
    def is_comment(self):
        # You can implement additional logic to differentiate comments from other replies
        return self.parent is not None and self.parent.is_commentable

    def __str__(self):
        return f'{self.user.username}: {self.text[:50]}...'
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_hashtags()

    def _update_hashtags(self):
        hashtag_names = set(part[1:] for part in self.text.split() if part.startswith('#'))
        existing_hashtags = Hashtag.objects.filter(name__in=hashtag_names)
        new_hashtag_names = hashtag_names - set(existing_hashtags.values_list('name', flat=True))
        new_hashtags = [Hashtag(name=name) for name in new_hashtag_names]
        Hashtag.objects.bulk_create(new_hashtags)

        all_hashtags = list(existing_hashtags) + new_hashtags
        self.hashtags.set(all_hashtags)
    