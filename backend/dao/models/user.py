# Django Imports
from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone
from django.db.models import Q

from .file import Image
from .flake import Flake, Like, Retweet # Import Retweet model

class User(models.Model):
    id = models.AutoField(primary_key=True)
    auth = models.OneToOneField(
        AuthUser,
        on_delete=models.CASCADE,
    )
    creation_date = models.DateTimeField(default=timezone.now)
    profile_image = models.ForeignKey(
        Image,
        related_name='used_in_profile',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    banner_image = models.ForeignKey(
        Image,
        related_name='used_in_banner',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    nickname = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(null=True, blank=True)

    # TODO: Slides about design pattern here, pros and cons
    follows = models.ManyToManyField(
        'self',
        related_name = 'followers',
        related_query_name = 'follower',
        symmetrical=False,
    )

    def post_flake(self, content, image=None, reply_to=None):
        return Flake.objects.create(
            author = self,
            content = content,
            image = image,
            reply_to = reply_to
        )
    
    def delete_flake(self, flake):
        if flake.author == self:
            flake.delete()

## Add the list_flakes method to the User model
    def list_flakes(self):
        flakes = Flake.objects.filter(Q(author=self) & Q(reply_to__isnull=True))
        retweets = Retweet.objects.filter(user=self)
        merged = list(flakes) + list(retweets)
        return sorted(merged, key=lambda x: x.creation_date, reverse=True)
    
    def get_feeds(self):
        flakes = Flake.objects.filter((Q(author=self) | Q(author__follower=self)) & Q(reply_to__isnull=True))
        retweets = Retweet.objects.filter(Q(user=self) | Q(user__follower=self))
        merged = list(flakes) + list(retweets)
        return sorted(merged, key=lambda x: x.creation_date, reverse=True)

    def like(self, flake):
        try:
            Like.objects.get(user=self, flake=flake)
        except Like.DoesNotExist:
            Like.objects.create(
                user = self,
                flake = flake
            )
    
    def unlike(self, flake):
        try:
            like = Like.objects.get(user=self, flake=flake)
            like.delete()
        except Like.DoesNotExist:
            return

    def follow(self, followee):
        self.follows.add(followee)
        self.save()
    
    def unfollow(self, followee):
        self.follows.remove(followee)
        self.save()
    
    def get_follows(self):
        return self.follows.all()
    
    def get_followers(self):
        return self.followers.all()
    
## Add the retweet to the User model
    def retweet(self, flake):
        try:
            Retweet.objects.get(user=self, flake=flake)
        except Retweet.DoesNotExist:
            Retweet.objects.create(
                user=self,
                flake=flake
            )

## Add the unretweet to the User model
    def unretweet(self, flake):
        try:
            retweet = Retweet.objects.get(user=self, flake=flake)
            retweet.delete()
        except Retweet.DoesNotExist:
            return
