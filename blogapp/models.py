from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField
from phonenumber_field.modelfields import PhoneNumberField


# ==============================
# PROFILE MODEL
# ==============================
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    phone = PhoneNumberField(
        unique=True,
        blank=True,
        null=True
    )
    profile_picture = CloudinaryField(
        "profile_picture",
        blank=True,
        null=True,
        default="profile_pics/default"
    )

    def __str__(self):
        return self.user.username


# ==============================
# CATEGORY MODEL
# ==============================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ==============================
# POST MODEL
# ==============================
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title



class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.content[:30]
    

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
        