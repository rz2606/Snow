from django.db import models
from django.utils import timezone

from .file import Image

# TODO: Homework: Add Retweet functionality
# TODO: Sample solution

class Flake(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(
        'User',
        related_name = "flakes",
        related_query_name = "flake",
        on_delete=models.CASCADE,
    )
    creation_date = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    image = models.ForeignKey(
        Image,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    reply_to = models.ForeignKey(
        'self',
        related_name = "comments",
        related_query_name = "comment",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    retweet_of = models.ForeignKey(
        'self',
        related_name="retweets_of",
        related_query_name="retweet_of",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def get_likes(self):
        return self.likes.all()

    def get_comments(self):
        return self.comments.all()
    
    @property
    def retweets(self):
        return Retweet.objects.filter(flake=self)
    
    def get_retweets(self):
        return Flake.objects.filter(retweet_of=self)

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    creation_date = models.DateTimeField(default=timezone.now)
    flake = models.ForeignKey(
        Flake,
        related_name = "likes",
        related_query_name = "like",
        on_delete=models.CASCADE
    ) 

    class Meta:
        constraints = [models.UniqueConstraint("user", "flake", name="unique_like")]


class Retweet(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    creation_date = models.DateTimeField(default=timezone.now)
    flake = models.ForeignKey(
        Flake,
        related_name="retweets",
        related_query_name="retweet",
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [models.UniqueConstraint("user", "flake", name="unique_retweet")]